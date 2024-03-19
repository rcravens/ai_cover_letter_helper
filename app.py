import os

import openai as ai
import streamlit as st
from PyPDF2 import PdfReader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ai.api_key = os.getenv('OPENAI_API_KEY')
candidate_name = os.getenv('CANDIDATE_NAME')

# Initialize streamlit
st.set_page_config(page_title='Job Search Tools', page_icon='📝', layout='wide')
st.title('📝 Job Search Tools')

# Read resume data
resume_source = None
resume_text = ''
source_files = ['app_data.js', 'resume.txt', 'resume.pdf']
for source_file in source_files:
    if os.path.exists(source_file):
        resume_source = source_file
        if source_file.endswith('.pdf'):
            with open(source_file, 'rb') as f:
                pdf_reader = PdfReader(f)
                for page in pdf_reader.pages:
                    resume_text += page.extract_text()
        else:
            with open(source_file, 'r') as f:
                resume_text = f.readlines()
                resume_text = ''.join(resume_text)
    if len(resume_text) > 0:
        break

# Read candidate's sample writing style
sample_writing_style = ''
if os.path.exists('./sample_writing_style.txt'):
    with open('./sample_writing_style.txt', 'r') as sample_file:
        sample_writing_style = sample_file.readlines()
        sample_writing_style = ''.join(sample_writing_style)

# Summarize candidate data and LLM model
col1, col2 = st.columns(2)

with col1:
    st.subheader('Candidate Summary')
    st.write('Candidate Name: ' + candidate_name)
    st.write('Resume Source: ' + resume_source)
    st.write('Resume (word count):', len(resume_text.split()))
    st.write('Writing Style (word count): ', len(sample_writing_style.split()))

with col2:
    st.subheader('LLM Model')
    gpt_models = ['gpt-3.5-turbo', 'gpt-4']
    gpt_model = st.selectbox('Select GPT Model', options=gpt_models, index=0)
    temperature = st.number_input('AI Temperature', value=0.9)

# Tool to help generate summaries about the candidate's work experience
st.header('Experience Summarization')
with st.form('summarize'):
    prompt = st.text_input('Based on your resume, what would you like to summarize?')
    is_summary_in_my_writing_style = st.checkbox('Use my writing style', value=True)

    summarize_submitted = st.form_submit_button('Generate Summary')

    # Use the API to generate a cover letter
    if summarize_submitted:
        messages = [
            {'role': 'system', 'content': f'You are a talent agency and provide professional guidance to candidates based on the candidate\'s resume text and a prompt.'},
            {'role': 'system', 'content': f'All generated text should be written as if the candidate was writing it themself.'},
            {'role': 'system', 'content': f'The are helping a candidate summarize their work experience by answering questions about their experience'},
            {'role': 'user', 'content': f'The candidate\'s resume text: {resume_text}'},
            {'role': 'user', 'content': f'{prompt}'},
        ]
        if is_summary_in_my_writing_style:
            messages.append({'role': 'user', 'content': f'The candidate\'s writing style is: {sample_writing_style}'})
            messages.append({'role': 'user', 'content': f'The resulting summary should use the voice, tone, style, and structure of the candidate\'s writing style'})
            messages.append({'role': 'user', 'content': f'The resulting summary should only use information from the candidate\'s resume and not directly use content from the candidate\'s writing style.'})

        summary_result = ai.chat.completions.create(
            model=gpt_model,
            temperature=temperature,
            messages=messages,
        )

        summary = summary_result.choices[0].message.content
        st.write(summary)

# Tool to help generate cover letter drafts
st.header('Cover Letter Generation')
with st.form('input_form'):
    job_description = st.text_area('Pasted Job Description', height=200)
    job_title = st.text_input('Job Title', '[Job Title]')
    company = st.text_input('Company Name', '[Company Name]')
    manager = st.text_input('Hiring Manager', '[Hiring Manager]')
    source = st.text_input('Source of Job Description', '[Source]')
    additional_guidance = st.text_input('Additional Guidance', value='')
    is_cover_letter_in_my_writing_style = st.checkbox('Use my writing style', value=True)

    submitted = st.form_submit_button('Create Cover Letter')

    # Use OpenAI API to create cover letter
    if submitted:
        messages = [
            {'role': 'system', 'content': f'You are a talent agency and provide professional guidance to candidates based on the candidate\'s resume text and a prompt.'},
            {'role': 'system', 'content': f'All generated text should be written as if the candidate was writing it themselves.'},
            {'role': 'system', 'content': f'The generated text should be written as if a human was writing it themselves.'},
            {'role': 'system', 'content': f'You are helping a candidate generate a cover letter based on the following candidate resume and a job description.'},
            {'role': 'user', 'content': f'Generate a cover letter based on the following candidate\'s resume and job description.'},
            {'role': 'user', 'content': f'The candidate\'s name is: {candidate_name}'},
            {'role': 'user', 'content': f'The candidate\'s resume is: {resume_text}'},
            {'role': 'user', 'content': f'The job description is: {job_description}'},
            {'role': 'user', 'content': f'The job title is: {job_title}'},
            {'role': 'user', 'content': f'The hiring company is: {company}'},
            {'role': 'user', 'content': f'The hiring manager is: {manager}'},
            {'role': 'user', 'content': f'Source of job description is: {source}'},
            {'role': 'user', 'content': f'The resulting cover letter should include at least 3 paragraphs'},
            {'role': 'user', 'content': f'The first paragraph should focus on relaying interest in the posted job description.'},
            {'role': 'user', 'content': f'The middle paragraphs should focus on specific examples of why the candidate is a great fit.'},
            {'role': 'user', 'content': f'The last paragraph should restate interest, summarize what the candidate has to offer, and express some forward looking statement.'},
            {'role': 'user', 'content': f'The cover letter should be written like a real person created the content'},
        ]
        if is_cover_letter_in_my_writing_style:
            messages.append({'role': 'user', 'content': f'The candidate\'s writing style is: {sample_writing_style}'})
            messages.append({'role': 'user', 'content': f'The cover letter should use the voice, tone, style, and structure of the candidate\'s writing style'})
            messages.append({'role': 'user', 'content': f'The resulting cover letter should only use information from the candidate\'s resume and not directly use content from the candidate\'s writing style.'})

        if additional_guidance is not None and len(additional_guidance) > 0:
            messages.append({'role': 'user', 'content': f'In addition to the previous history, here is some additional guidance: {additional_guidance}'})

        response = ai.chat.completions.create(
            model=gpt_model,
            temperature=temperature,
            messages=messages,
        )

        cover_letter = response.choices[0].message.content
        st.write(cover_letter)
