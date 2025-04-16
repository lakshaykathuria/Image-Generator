# -*- coding: utf-8 -*-
"""Image Generator.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/15CDXOHg2TluDJZFsjcgsTps0Zj1DxoMa
"""

!pip install --upgrade diffusers transformers accelerate torch safetensors --quiet

import torch
from diffusers import StableDiffusionXLPipeline
torch.cuda.empty_cache()
# Load SDXL model (base version) with FP16 for faster processing
pipe = StableDiffusionXLPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float16,  # Enable FP16 precision for faster processing
    variant="fp16",             # Use FP16 variant for the model
    use_safetensors=True
).to("cuda")  # Ensure it's on GPU (CUDA)

prompt = "a hyperrealistic photo of a lion wearing a crown, golden hour lighting"

# Generate the image (single image at a time)
image = pipe(prompt=prompt).images[0]

# Show and save the result
image.show()
image.save("lion_with_crown_sdxl.png")
# Clear GPU memory after generation (optional but recommended)
torch.cuda.empty_cache()

!pip install gradio --quiet

import gradio as gr

# Map selected style to style-specific suffix
style_keywords = {
    "Realistic": "ultra realistic, 4K, photo style, cinematic lighting",
    "Cartoon": "cartoon style, bold outlines, simple shading",
    "Anime": "anime style, vibrant colors, cel shading",
    "Oil Painting": "oil painting style, textured brush strokes",
    "3D Render": "3D render, highly detailed, studio lighting"
}

def generate_image(prompt, style):
    # Style keywords for realism + alternatives
    style_keywords = {
        "Realistic": "high-resolution, 8K, DSLR photo, real skin texture, sharp focus, cinematic lighting, natural colors",
        "Cartoon": "cartoon style, bold outlines, flat shading",
        "Anime": "anime style, colorful, smooth skin, cel shading",
        "Oil Painting": "oil painting style, brush strokes, traditional canvas look",
        "3D Render": "3D render, soft shadows, digital lighting"
    }

    # Strong negative prompt to avoid toy-like/artifacts
    negative_prompt = (
        "blurry, cartoon, 3D, illustration, bad anatomy, low quality, fake, distorted, watermark, text, extra fingers"
    )

    # Enhance the main prompt
    full_prompt = f"{prompt}, {style_keywords[style]}"

    image = pipe(
        prompt=full_prompt,
        negative_prompt=negative_prompt,
        guidance_scale=9.0,           # more accurate to text
        num_inference_steps=60        # more refined output
    ).images[0]

    return image


# Build the UI
with gr.Blocks() as demo:
    gr.Markdown("## 🎯 ImageGenie — Create Stunning Images from Text with Style")

    with gr.Row():
        prompt_input = gr.Textbox(label="Prompt", placeholder="e.g. an elephant solving a mystery in the city")
        style_input = gr.Dropdown(choices=list(style_keywords.keys()), value="Realistic", label="Choose Style")

    output = gr.Image(label="Generated Image")
    generate_btn = gr.Button("🚀 Generate")

    generate_btn.click(fn=generate_image, inputs=[prompt_input, style_input], outputs=output)

demo.launch(share=True)