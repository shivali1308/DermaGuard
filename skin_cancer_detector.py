import gradio as gr
from transformers import AutoModelForImageClassification, AutoImageProcessor
from PIL import Image
import torch

# Load the model and processor from Hugging Face
repo_name = "Jayanth2002/dinov2-base-finetuned-SkinDisease"
image_processor = AutoImageProcessor.from_pretrained(repo_name)
model = AutoModelForImageClassification.from_pretrained(repo_name)

# Filter to only skin cancer related classes
skin_cancer_classes = {
    'Basal Cell Carcinoma': 'Basal Cell Carcinoma',
    'Melanoma': 'Melanoma', 
    'squamous cell carcinoma': 'Squamous Cell Carcinoma',
    'actinic keratosis': 'Actinic Keratosis',  # Pre-cancerous
    'nevus': 'Benign Mole (No Cancer)',
    'dermatofibroma': 'Benign (No Cancer)',
    'pigmented benign keratosis': 'Benign (No Cancer)',
    'seborrheic keratosis': 'Benign (No Cancer)',
    'vascular lesion': 'Benign (No Cancer)'
}

# Map all other non-cancer classes to "No Cancer"
other_classes_to_no_cancer = [
    'Darier_s Disease', 'Epidermolysis Bullosa Pruriginosa', 'Hailey-Hailey Disease',
    'Herpes Simplex', 'Impetigo', 'Larva Migrans', 'Leprosy Borderline', 
    'Leprosy Lepromatous', 'Leprosy Tuberculoid', 'Lichen Planus', 
    'Lupus Erythematosus Chronicus Discoides', 'Molluscum Contagiosum', 
    'Mycosis Fungoides', 'Neurofibromatosis', 'Papilomatosis Confluentes And Reticulate',
    'Pediculosis Capitis', 'Pityriasis Rosea', 'Porokeratosis Actinic', 
    'Psoriasis', 'Tinea Corporis', 'Tinea Nigra', 'Tungiasis'
]

# Original class names from the model
original_class_names = ['Basal Cell Carcinoma', 'Darier_s Disease', 'Epidermolysis Bullosa Pruriginosa', 'Hailey-Hailey Disease', 'Herpes Simplex', 'Impetigo', 'Larva Migrans', 'Leprosy Borderline', 'Leprosy Lepromatous', 'Leprosy Tuberculoid', 'Lichen Planus', 'Lupus Erythematosus Chronicus Discoides', 'Melanoma', 'Molluscum Contagiosum', 'Mycosis Fungoides', 'Neurofibromatosis', 'Papilomatosis Confluentes And Reticulate', 'Pediculosis Capitis', 'Pityriasis Rosea', 'Porokeratosis Actinic', 'Psoriasis', 'Tinea Corporis', 'Tinea Nigra', 'Tungiasis', 'actinic keratosis', 'dermatofibroma', 'nevus', 'pigmented benign keratosis', 'seborrheic keratosis', 'squamous cell carcinoma', 'vascular lesion']

# Prediction function with confidence scores
def predict(image):
    # Preprocess the image
    encoding = image_processor(image.convert("RGB"), return_tensors="pt")
    
    # Get model predictions
    with torch.no_grad():
        outputs = model(**encoding)
    
    # Get probabilities using softmax
    probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
    
    # Get top 3 predictions
    top3_probs, top3_indices = torch.topk(probabilities, 3)
    
    results = []
    for i in range(3):
        original_class = original_class_names[top3_indices[0][i].item()]
        probability = top3_probs[0][i].item() * 100
        
        # Map to skin cancer categories
        if original_class in skin_cancer_classes:
            mapped_class = skin_cancer_classes[original_class]
        else:
            # Map all other diseases to "No Cancer" or "Other Skin Condition"
            if any(cancer_term in original_class.lower() for cancer_term in ['carcinoma', 'melanoma', 'cancer']):
                mapped_class = "Other Skin Condition"
            else:
                mapped_class = "No Cancer"
        
        results.append({
            'disease': mapped_class,
            'confidence': probability,
            'original_class': original_class
        })
    
    # Format the output
    output_text = "🔍 AI Skin Cancer Analysis Results:\n\n"
    
    for i, result in enumerate(results):
        status_icon = "🟢" if "No Cancer" in result['disease'] else "🟡" if "Benign" in result['disease'] else "🔴"
        output_text += f"{status_icon} {result['disease']}: {result['confidence']:.1f}%\n"
    
    # Add medical disclaimer
    output_text += "\n-----\n"
    output_text += "⚠️ **Important Disclaimer:** This AI tool is for educational purposes only. Always consult a qualified dermatologist for proper diagnosis and treatment."
    
    return output_text

# Custom CSS for better appearance
custom_css = """
#skin-cancer-app {
    max-width: 800px;
    margin: 0 auto;
}
.result-box {
    padding: 20px;
    border-radius: 10px;
    margin: 10px 0;
}
.high-risk { background-color: #fee2e2; border-left: 4px solid #dc2626; }
.medium-risk { background-color: #fef3c7; border-left: 4px solid #d97706; }
.low-risk { background-color: #d1fae5; border-left: 4px solid #059669; }
"""

# Create Gradio interface
with gr.Blocks(css=custom_css, title="AI Skin Cancer Detector") as demo:
    gr.Markdown("""
    # 🩺 AI Skin Cancer Detection
    ### Early Detection for Basal Cell Carcinoma, Squamous Cell Carcinoma, and Melanoma
    """)
    
    with gr.Row():
        with gr.Column():
            image_input = gr.Image(
                type="pil", 
                label="Upload Skin Image",
                info="Upload a clear image of the skin area of concern"
            )
            submit_btn = gr.Button("🔬 Analyze Image", variant="primary")
        
        with gr.Column():
            output_text = gr.Textbox(
                label="Analysis Results",
                lines=10,
                max_lines=15,
                show_copy_button=True
            )
    
    # Examples section
    gr.Markdown("### 📋 Example Images You Can Test")
    gr.Examples(
        examples=[
            ["example_melanoma.jpg"],  # You can add example images here
            ["example_bcc.jpg"],
            ["example_scc.jpg"],
            ["example_benign.jpg"]
        ],
        inputs=image_input,
        outputs=output_text,
        fn=predict,
        cache_examples=False
    )
    
    # Medical disclaimer
    gr.Markdown("""
    ---
    ### ⚠️ Medical Disclaimer
    This AI tool is designed for **educational and awareness purposes only**. It is not a substitute for professional medical diagnosis, advice, or treatment. Always seek the advice of a qualified healthcare provider with any questions you may have regarding a medical condition.
    
    **Key Limitations:**
    - AI models can make errors
    - Early-stage cancers may be missed
    - Image quality affects accuracy
    - Regular medical checkups are essential
    """)
    
    # Connect the interface
    submit_btn.click(
        fn=predict,
        inputs=image_input,
        outputs=output_text
    )
    
    # Also predict on image upload
    image_input.upload(
        fn=predict,
        inputs=image_input,
        outputs=output_text
    )

# Launch the interface
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",  # Allow external access
        share=True,  # Create a public link
        debug=True   # Show errors
    )