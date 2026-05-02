package main

import (
	"crypto/ecdsa"
	"crypto/elliptic"
	"crypto/rand"
	"crypto/x509"
	"crypto/x509/pkix"
	"encoding/pem"
	"fmt"
	"io/ioutil"
	"log"
	"math/big"
	"net"
	"net/http"
	"os"
	"os/exec"
	"strings"
	"text/template"
	"time"
)

type CaddyfileContext struct {
	LocalIP          string
	InternetIP       string
	LocalIPDashed    string
	InternetIPDashed string
	IPDomain         string
}

func main() {

	ipDomain := os.Getenv("IP_DOMAIN")
	if ipDomain == "" {
		log.Fatalf("IP_DOMAIN environment variable not set")
	}

	// Get local IP address
	localIP, err := getLocalIP()
	if err != nil {
		log.Fatalf("Failed to get local IP: %v", err)
	}

	// Get internet IP address
	internetIP, err := getInternetIP()
	if err != nil {
		log.Fatalf("Failed to get internet IP: %v", err)
	}

	localIPDashed := strings.ReplaceAll(localIP, ".", "-")
	internetIPDashed := strings.ReplaceAll(internetIP, ".", "-")

	CaddyfileContext := CaddyfileContext{
		LocalIP:          localIP,
		InternetIP:       internetIP,
		LocalIPDashed:    localIPDashed,
		InternetIPDashed: internetIPDashed,
		IPDomain:         ipDomain,
	}

	// Generate self-signed certificate if it doesn't exist
	_, err = os.Stat("cert.pem")
	if err == nil {
		log.Printf("Certificate already exists")
	} else {
		log.Printf("Generating self-signed certificate")
		err = generateSelfSignedCert(localIP, internetIP, ipDomain)
		if err != nil {
			log.Fatalf("Failed to generate self-signed certificate: %v", err)
		}
	}

	// generate Caddyfile from template
	caddyfile, err := os.ReadFile("Caddyfile.tmpl")
	if err != nil {
		log.Fatalf("Failed to read Caddyfile template: %v", err)
	}

	// file context for Caddyfile
	caddyfileContent := string(caddyfile)
	// use template engine

	tmpl, err := template.New("Caddyfile").Parse(caddyfileContent)
	if err != nil {
		log.Fatalf("Failed to parse Caddyfile template: %v", err)
	}

	// output Caddyfile to file
	os.Remove("Caddyfile")
	file, err := os.Create("Caddyfile")
	if err != nil {
		log.Fatalf("Failed to create Caddyfile: %v", err)
	}
	defer file.Close()

	err = tmpl.Execute(file, CaddyfileContext)
	if err != nil {
		log.Fatalf("Failed to execute Caddyfile template: %v", err)
	}

	log.Printf("Caddyfile generated successfully")

	if len(os.Args) > 1 && os.Args[1] == "run" {
		log.Printf("Starting Caddy server")
		cmd := exec.Command("caddy", "run")
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr
		err = cmd.Run()
		if err != nil {
			log.Fatalf("Failed to start Caddy server: %v", err)
		}
	}
}

func getLocalIP() (string, error) {
	interfaces, err := net.Interfaces()
	if err != nil {
		return "", err
	}

	for _, iface := range interfaces {
		if iface.Flags&net.FlagUp != 0 && iface.Flags&net.FlagLoopback == 0 {
			addrs, err := iface.Addrs()
			if err != nil {
				return "", err
			}
			for _, addr := range addrs {
				var ip net.IP
				switch v := addr.(type) {
				case *net.IPNet:
					ip = v.IP
				case *net.IPAddr:
					ip = v.IP
				}
				if ip != nil && ip.To4() != nil {
					return ip.String(), nil
				}
			}
		}
	}
	return "", fmt.Errorf("no connected network interface found")
}

func getInternetIP() (string, error) {
	resp, err := http.Get("https://1.1.1.1/cdn-cgi/trace")
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}

	for _, line := range strings.Split(string(body), "\n") {
		if strings.HasPrefix(line, "ip=") {
			return strings.TrimPrefix(line, "ip="), nil
		}
	}
	return "", fmt.Errorf("could not find internet IP address")
}

func generateSelfSignedCert(localIP, internetIP, ipDomain string) error {
	priv, err := ecdsa.GenerateKey(elliptic.P256(), rand.Reader)
	if err != nil {
		return err
	}

	notBefore := time.Now()
	notAfter := notBefore.Add(365 * 24 * time.Hour)

	serialNumber, err := rand.Int(rand.Reader, new(big.Int).Lsh(big.NewInt(1), 128))
	if err != nil {
		return err
	}

	localIPDashed := strings.ReplaceAll(localIP, ".", "-")
	internetIPDashed := strings.ReplaceAll(internetIP, ".", "-")

	template := x509.Certificate{
		SerialNumber: serialNumber,
		Subject: pkix.Name{
			Organization: []string{"cuda-container"},
		},
		NotBefore: notBefore,
		NotAfter:  notAfter,

		KeyUsage:              x509.KeyUsageKeyEncipherment | x509.KeyUsageDigitalSignature,
		ExtKeyUsage:           []x509.ExtKeyUsage{x509.ExtKeyUsageServerAuth},
		BasicConstraintsValid: true,
		IPAddresses:           []net.IP{net.ParseIP(localIP), net.ParseIP(internetIP)},
		DNSNames:              []string{fmt.Sprintf("*.%s", ipDomain), fmt.Sprintf("*.%s.%s", internetIPDashed, ipDomain), fmt.Sprintf("*.%s.%s", localIPDashed, ipDomain)},
	}

	derBytes, err := x509.CreateCertificate(rand.Reader, &template, &template, &priv.PublicKey, priv)
	if err != nil {
		return err
	}

	certOut, err := os.Create("cert.pem")
	if err != nil {
		return err
	}
	defer certOut.Close()

	if err := pem.Encode(certOut, &pem.Block{Type: "CERTIFICATE", Bytes: derBytes}); err != nil {
		return err
	}

	keyOut, err := os.Create("key.pem")
	if err != nil {
		return err
	}
	defer keyOut.Close()

	privBytes, err := x509.MarshalECPrivateKey(priv)
	if err != nil {
		return err
	}

	if err := pem.Encode(keyOut, &pem.Block{Type: "EC PRIVATE KEY", Bytes: privBytes}); err != nil {
		return err
	}

	return nil
}
