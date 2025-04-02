Math Solving Assistant
1. Overview
We have developed Math Solving Assistant, a chatbot website designed to help users solve mathematical problems, chat with an AI assistant, and analyze images. The platform is built using Gemini’s API, written in Python, and powered by Streamlit for the user interface.

The product is live at: 

User Interface Overview


The left panel features the navigation menu, allowing users to switch between different functionalities.

Below the menu, users can upload images for OCR-based problem-solving.

The right side serves as the main interface for chatting with the AI and solving math problems.

2. Key Features
Our product includes three main functionalities:

1. Chat with Gemini
Users can interact with Gemini Pro 1.0, asking general questions, seeking explanations, or translating text. The chatbot also integrates an OCR feature, allowing users to upload images of math problems, which are then converted into text for Gemini to analyze.

Screenshots:
Chat Interface:


OCR-based Math Input:


Current Limitations:

While the chatbot performs well, it sometimes provides inaccurate or inconsistent responses.

To improve accuracy, we are fine-tuning Gemini with a specialized math dataset.

2. Image Analysis
This feature leverages Gemini Pro Vision’s API to analyze uploaded images and describe their contents. It serves as a supplementary tool for users who need assistance with visual data interpretation.

Screenshot:


3. Math Problem Assistance
The core feature of our product helps users solve mathematical problems. While Gemini Pro 1.0 already performs well, its accuracy can be inconsistent. To enhance reliability, we are fine-tuning Gemini with the MetaMathQA-40K dataset.

Fine-Tuning Process
The MetaMathQA-40K dataset consists of 40,000 math problems sourced from MetaMath on Hugging Face.

Fine-tuning is conducted on Google Cloud Platform’s Vertex AI, following these steps:

Converting the dataset into JSONL format for training.

Uploading the dataset to Vertex AI.

Creating a custom-tuned model for enhanced math problem-solving.

Screenshots:
Fine-Tuning Setup:


Dataset Upload & Processing:


Fine-Tuning in Progress:


4. Performance Comparison: Before vs. After Fine-Tuning
Original Model	Fine-Tuned Model
	
The fine-tuned model delivers significantly more accurate and stable responses.

Through multiple test cases, we found that the model now handles complex math queries with higher precision and reliability.

5. Conclusion
With Math Solving Assistant, we aim to provide a powerful, AI-driven tool for solving math problems. The fine-tuned Gemini model improves accuracy, stability, and problem-solving capabilities, making it a valuable resource for students and educators alike.

Our future updates will focus on:
✅ Further enhancing response quality.
✅ Expanding dataset coverage for different types of math problems.
✅ Introducing step-by-step problem-solving explanations.

Try the tool now: 

