package main

import (
	"bytes"
	"crypto"
	"crypto/rsa"
	"crypto/sha1"
	"crypto/x509"
	"encoding/base64"
	"encoding/json"
	"encoding/pem"
	"io"
	"log"
	"net/http"
	"net/url"
	"strings"
	"sync"
	"time"
)

var (
	certCache  = make(map[string]certCacheEntry)
	cacheMutex sync.RWMutex
)

// AlexaRequest represents the incoming request from Alexa
type AlexaRequest struct {
	Version string `json:"version"`
	Session struct {
		Application struct {
			ApplicationID string `json:"applicationId"`
		} `json:"application"`
	} `json:"session"`
	Request struct {
		Type      string    `json:"type"`
		Timestamp string    `json:"timestamp"`
		Intent    *struct { // Optional for non-intent requests
			Name  string `json:"name"`
			Slots map[string]struct {
				Value string `json:"value"`
			} `json:"slots"`
		} `json:"intent,omitempty"`
	} `json:"request"`
}

// AlexaResponse represents the response to send back to Alexa
type AlexaResponse struct {
	Version  string `json:"version"`
	Response struct {
		OutputSpeech struct {
			Type string `json:"type"`
			Text string `json:"text"`
		} `json:"outputSpeech"`
		ShouldEndSession bool `json:"shouldEndSession"`
		Reprompt         *struct {
			OutputSpeech struct {
				Type string `json:"type"`
				Text string `json:"text"`
			} `json:"outputSpeech"`
		} `json:"reprompt,omitempty"`
	} `json:"response"`
}

type certCacheEntry struct {
	certificates []*x509.Certificate
	expiry       time.Time
}

func validateAlexaRequest(r *http.Request, expectedAppID string) bool {
	signature := r.Header.Get("Signature")
	certURL := r.Header.Get("SignatureCertChainUrl")

	if signature == "" || certURL == "" {
		log.Println("Request missing signature or certificate URL")
		return false
	}

	parsedURL, err := url.Parse(certURL)
	if err != nil {
		log.Printf("Invalid certificate URL: %s", certURL)
		return false
	}

	if parsedURL.Scheme != "https" ||
		parsedURL.Host != "s3.amazonaws.com" ||
		!strings.HasPrefix(parsedURL.Path, "/echo.api/") ||
		parsedURL.Port() != "" && parsedURL.Port() != "443" {
		log.Printf("Invalid certificate URL: %s", certURL)
		return false
	}

	// Read request body for verification
	bodyBytes, err := io.ReadAll(r.Body)
	if err != nil {
		log.Printf("Failed to read request body: %v", err)
		return false
	}
	r.Body = io.NopCloser(bytes.NewBuffer(bodyBytes))

	// Get certificate and verify signature
	var certificates []*x509.Certificate
	var exists bool
	var cacheEntry certCacheEntry

	cacheMutex.RLock()
	cacheEntry, exists = certCache[certURL]
	cacheMutex.RUnlock()

	// Check if we have a valid cached certificate
	if exists && time.Now().Before(cacheEntry.expiry) {
		certificates = cacheEntry.certificates
	} else {
		// Fetch and validate certificates
		resp, err := http.Get(certURL)
		if err != nil {
			log.Printf("Failed to get certificate: %v", err)
			return false
		}
		defer resp.Body.Close()

		certBytes, err := io.ReadAll(resp.Body)
		if err != nil {
			log.Printf("Failed to read certificate: %v", err)
			return false
		}

		// Parse the certificate chain
		var block *pem.Block
		for {
			block, certBytes = pem.Decode(certBytes)
			if block == nil {
				break
			}
			cert, err := x509.ParseCertificate(block.Bytes)
			if err != nil {
				log.Printf("Failed to parse certificate: %v", err)
				return false
			}
			certificates = append(certificates, cert)
		}

		if len(certificates) == 0 {
			log.Println("No certificates found in response")
			return false
		}

		// Validate certificates
		for _, cert := range certificates {
			// Check expiration
			now := time.Now()
			if now.Before(cert.NotBefore) || now.After(cert.NotAfter) {
				log.Printf("Certificate is not valid at current time. NotBefore: %v, NotAfter: %v",
					cert.NotBefore, cert.NotAfter)
				return false
			}

			// Check if the certificate is issued for echo-api.amazon.com
			validDomain := false
			for _, name := range cert.DNSNames {
				if name == "echo-api.amazon.com" {
					validDomain = true
					break
				}
			}
			if !validDomain && len(cert.DNSNames) > 0 {
				log.Printf("Certificate not issued for echo-api.amazon.com. DNSNames: %v", cert.DNSNames)
				return false
			}
		}

		intermediates := x509.NewCertPool()
		if len(certificates) > 1 {
			for i := 1; i < len(certificates); i++ {
				intermediates.AddCert(certificates[i])
			}
		}

		opts := x509.VerifyOptions{
			Intermediates: intermediates,
		}

		if _, err := certificates[0].Verify(opts); err != nil {
			log.Printf("Certificate verification failed: %v", err)
			return false
		}

		// Cache the certificates with an expiration (24 hours)
		cacheMutex.Lock()
		certCache[certURL] = certCacheEntry{
			certificates: certificates,
			expiry:       time.Now().Add(24 * time.Hour),
		}
		cacheMutex.Unlock()
	}

	// Verify signature
	signatureBytes, err := base64.StdEncoding.DecodeString(signature)
	if err != nil {
		log.Printf("Failed to decode signature: %v", err)
		return false
	}

	if len(certificates) == 0 {
		log.Println("No certificates available for signature verification")
		return false
	}

	leafCert := certificates[0]
	publicKey, ok := leafCert.PublicKey.(*rsa.PublicKey)
	if !ok {
		log.Println("Certificate public key is not RSA")
		return false
	}

	hash := sha1.Sum(bodyBytes)
	err = rsa.VerifyPKCS1v15(publicKey, crypto.SHA1, hash[:], signatureBytes)
	if err != nil {
		log.Printf("Signature verification failed: %v", err)
		return false
	}

	var alexaReq AlexaRequest
	if err := json.Unmarshal(bodyBytes, &alexaReq); err != nil {
		log.Printf("Failed to parse request JSON: %v", err)
		return false
	}

	// Check timestamp (within 150 seconds)
	timestamp := alexaReq.Request.Timestamp
	if timestamp == "" {
		log.Println("Request missing timestamp")
		return false
	}

	requestTime, err := time.Parse(time.RFC3339, timestamp)
	if err != nil {
		log.Printf("Invalid timestamp format: %v", err)
		return false
	}

	currentTime := time.Now()
	if currentTime.Sub(requestTime).Abs().Seconds() > 150 {
		log.Printf("Request too old: %s", timestamp)
		return false
	}

	appID := alexaReq.Session.Application.ApplicationID

	if appID != expectedAppID {
		log.Printf("Invalid application ID: %s", appID)
		return false
	}

	return true
}

func parseAlexaRequest(requestBody []byte) (string, map[string]string) {
	var alexaReq AlexaRequest
	slots := make(map[string]string)

	if err := json.Unmarshal(requestBody, &alexaReq); err != nil {
		log.Printf("Error parsing Alexa request: %v", err)
		return "", slots
	}

	intentName := alexaReq.Request.Type
	if intentName == "IntentRequest" && alexaReq.Request.Intent != nil {
		intentName = alexaReq.Request.Intent.Name

		// Extract slots
		if alexaReq.Request.Intent.Slots != nil {
			for slotName, slotData := range alexaReq.Request.Intent.Slots {
				slots[slotName] = slotData.Value
			}
		}
	}

	return intentName, slots
}

func buildAlexaResponse(speechText string, shouldEndSession bool, repromptText string) AlexaResponse {
	response := AlexaResponse{
		Version: "1.0",
	}

	response.Response.OutputSpeech.Type = "PlainText"
	response.Response.OutputSpeech.Text = speechText
	response.Response.ShouldEndSession = shouldEndSession

	if repromptText != "" {
		response.Response.Reprompt = &struct {
			OutputSpeech struct {
				Type string `json:"type"`
				Text string `json:"text"`
			} `json:"outputSpeech"`
		}{
			OutputSpeech: struct {
				Type string `json:"type"`
				Text string `json:"text"`
			}{
				Type: "PlainText",
				Text: repromptText,
			},
		}
	}

	return response
}
