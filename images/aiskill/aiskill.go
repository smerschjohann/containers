package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log/slog"
	"net/http"
	"os"

	"google.golang.org/genai"
)

// Global variables
var (
	geminiClient *genai.Client
	chat         *genai.Chat
	modelName    string
)

func askGemini(prompt string) (string, error) {
	ctx := context.Background()

	if chat == nil {
		history := []*genai.Content{}
		var err error
		chat, err = geminiClient.Chats.Create(ctx,
			modelName,
			&genai.GenerateContentConfig{
				SystemInstruction: genai.NewContentFromText("Halte dich kurz aber informativ, maximal 120 Worte. Keine Begrüßung.", genai.RoleModel),
			},
			history,
		)
		if err != nil {
			return "", err
		}
	}

	response, err := chat.SendMessage(ctx, genai.Part{Text: prompt})
	if err != nil {
		return "", err
	}

	if len(response.Candidates) == 0 {
		return "", fmt.Errorf("no candidates in response")
	}

	part := response.Candidates[0].Content.Parts[0]
	return part.Text, nil
}

func handleAlexaRequest(w http.ResponseWriter, r *http.Request) {
	// Read request body
	bodyBytes, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "Failed to read request body", http.StatusInternalServerError)
		return
	}
	r.Body = io.NopCloser(bytes.NewBuffer(bodyBytes)) // Restore for other handlers

	slog.Info("Received Alexa request", "body", string(bodyBytes))

	intentName, slots := parseAlexaRequest(bodyBytes)
	slog.Info("Parsed Alexa request", "intent_name", intentName, "slots", slots)

	var alexaResponse AlexaResponse

	switch intentName {
	case "CaptureSentenceIntent":
		spokenSentence, ok := slots["spokenSentence"]
		speechText := ""

		if !ok {
			slog.Error("Slot 'spokenSentence' not found")
		}
		// if ok {
		// 	speechText = fmt.Sprintf("Du hast gesagt: %s.", spokenSentence)
		// }

		geminiResponse, err := askGemini(spokenSentence)
		if err != nil {
			slog.Error("Error calling Gemini API", "error", err)
			speechText += " Entschuldigung, ich konnte keine Antwort generieren."
		} else {
			speechText += " " + geminiResponse
		}

		alexaResponse = buildAlexaResponse(speechText, false, "Fahre fort")

	case "AMAZON.LaunchIntent", "LaunchRequest":
		chat = nil // Clear conversation history
		alexaResponse = buildAlexaResponse("Hi!", false, "")

	case "AMAZON.HelpIntent":
		alexaResponse = buildAlexaResponse("Du kannst mir einen Satz sagen, und ich werde ihn verarbeiten.", false, "")

	case "AMAZON.CancelIntent", "AMAZON.StopIntent", "SessionEndedRequest":
		alexaResponse = buildAlexaResponse("Auf Wiedersehen!", true, "")

	case "AMAZON.FallbackIntent":
		alexaResponse = buildAlexaResponse("Bitte benutze ein Triggerwort.", false, "")

	default:
		alexaResponse = buildAlexaResponse("Entschuldigung, ich habe das nicht verstanden.", false, "")
	}

	slog.Info("Sending Alexa response", "response", alexaResponse)
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(alexaResponse)
}

func main() {
	// Initialize Gemini client
	ctx := context.Background()
	apiKey := os.Getenv("GEMINI_API_KEY")
	if apiKey == "" {
		slog.Error("GEMINI_API_KEY environment variable not set")
		return
	}

	skillId := os.Getenv("ALEXA_SKILL_ID")
	if skillId == "" {
		slog.Error("ALEXA_SKILL_ID environment variable not set")
		return
	}

	// Set model name with default
	modelName = os.Getenv("GEMINI_MODEL")
	if modelName == "" {
		modelName = "gemini-2.5-flash"
	}
	slog.Info("Using Gemini model", "model", modelName)

	var err error
	geminiClient, err = genai.NewClient(ctx, &genai.ClientConfig{
		APIKey:  apiKey,
		Backend: genai.BackendGeminiAPI,
	})
	if err != nil {
		slog.Error("Failed to create Gemini client", "error", err)
		return
	}

	// Set up HTTP server
	http.HandleFunc("/healthz", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(200)
		w.Write([]byte("ok"))
	})
	http.HandleFunc("/alexa", func(w http.ResponseWriter, r *http.Request) {
		// Validate request
		if !validateAlexaRequest(r, skillId) {
			http.Error(w, "Invalid request", http.StatusBadRequest)
			return
		}

		handleAlexaRequest(w, r)
	})

	// Run server
	port := 9409
	slog.Info("Starting server on port", "port", port)
	if err := http.ListenAndServe(fmt.Sprintf("0.0.0.0:%d", port), nil); err != nil {
		slog.Error("Failed to start server", "error", err)
		return
	}
}
