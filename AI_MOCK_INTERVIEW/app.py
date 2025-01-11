
import streamlit as st
import cv2
import numpy as np
from collections import deque
import time
import google.generativeai as genai
from fer import FER  # Emotion detection library
import speech_recognition as sr  # For speech-to-text

# Backend Code
class EmotionDetector:
    def __init__(self, buffer_size=30):
        """Initialize the emotion detector with specified settings."""
        self.detector = FER(mtcnn=True)  # More accurate face detection
        self.emotions_buffer = deque(maxlen=buffer_size)
        self.emotion_colors = {
            'angry': (0, 0, 255),    # Red
            'disgust': (0, 140, 255),  # Orange
            'fear': (0, 255, 255),   # Yellow
            'happy': (0, 255, 0),    # Green
            'sad': (255, 0, 0),      # Blue
            'surprise': (255, 0, 255),# Purple
            'neutral': (128, 128, 128)# Gray
        }
        
    def process_frame(self, frame):
        """Process a single frame and return emotion predictions."""
        try:
            result = self.detector.detect_emotions(frame)
            if not result:  # No face detected
                return frame, None
                
            # Get the first face detected
            face = result[0]
            emotions = face['emotions']
            bounding_box = face['box']
            
            # Draw bounding box
            x, y, w, h = bounding_box
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 255), 2)
            
            # Find dominant emotion
            dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0]
            self.emotions_buffer.append(dominant_emotion)
            
            # Draw emotion label with confidence
            emotion_text = f"{dominant_emotion}: {emotions[dominant_emotion]:.2f}"
            cv2.putText(frame, emotion_text, (x, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                       self.emotion_colors[dominant_emotion], 2)
            
            return frame, emotions
            
        except Exception as e:
            print(f"Error processing frame: {str(e)}")
            return frame, None

# Speech-to-Text Function
def recognize_speech():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    try:
        with mic as source:
            st.info("Listening for your answer...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=25)
            st.info("Processing your answer...")
            return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Could not understand the speech."
    except sr.RequestError:
        return "Error with the speech recognition service."
    except Exception as e:
        return f"Error: {str(e)}"

# Frontend Code
def main():
    st.title("AI-Powered Emotion-Aware Interview System")
    st.write("This system analyzes your emotions during an interview and evaluates your answers.")

    # Step 1: Ask for job title
    job_title = st.text_input("Enter the job title you are interviewing for:")
    if not job_title:
        st.stop()

    # Step 2: Set up Gemini API
    GEMINI_API_KEY = "AIzaSyDTYvKY2RFaAZlCxwPPIcXit15DNLxZlnY"  # Replace with your Gemini API key
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')

    # Step 3: Initialize EmotionDetector
    emotion_detector = EmotionDetector()

    # Step 4: Generate interview questions using Gemini API
    def generate_interview_question(job_title):
        prompt = f"Generate a professional interview question for a {job_title} role."
        response = model.generate_content(prompt)
        return response.text

    # Step 5: Start the interview
    if st.button("Start Interview"):
        st.write("The interview will begin now. Each question will have a 10-second response time.")
        st.write("Answer each question verbally, and your response will be evaluated.")

        # Start video capture
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            st.error("Error: Could not open webcam.")
            st.stop()

        # Ask 10 questions
        for i in range(1, 3):
            st.write(f"Question {i}:")
            question = generate_interview_question(job_title)
            st.write(question)

            # Record emotions during the question
            start_time = time.time()
            emotions_during_question = []
            video_placeholder = st.empty()

            while time.time() - start_time < 25:  # 10 seconds for each question
                ret, frame = cap.read()
                if not ret:
                    st.error("Error: Could not read frame.")
                    break

                # Process frame for emotion detection
                processed_frame, emotions = emotion_detector.process_frame(frame)
                if emotions:
                    dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0]
                    emotions_during_question.append(dominant_emotion)

                # Display the processed frame
                video_placeholder.image(processed_frame, channels="BGR", use_column_width=True)

            # Speech-to-text for the answer
            answer = recognize_speech()
            st.write(f"Your Answer: {answer}")

            # Evaluate the answer using Gemini API
            evaluation_prompt = f"Evaluate this answer for a {job_title} role: {answer}"
            evaluation_response = model.generate_content(evaluation_prompt)
            st.write(f"Answer Evaluation: {evaluation_response.text}")

            # Calculate emotion statistics for the question
            if emotions_during_question:
                emotion_stats = {}
                total_responses = len(emotions_during_question)
                for emotion in emotion_detector.emotion_colors.keys():
                    count = emotions_during_question.count(emotion)
                    emotion_stats[emotion] = (count / total_responses) * 100

                # Display statistics
                st.write("Emotion Statistics for this question:")
                st.bar_chart(emotion_stats)

        # Release the camera
        cap.release()
        st.success("Interview Completed!")

if __name__ == "__main__":
    main()
