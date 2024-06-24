from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain import PromptTemplate


map_prompt = """
Summarize the main points and their comprehensive explanations from below text, presenting them under appropriate headings. Use various Emoji to symbolize different sections, and format the content as a cohesive paragraph under each heading. Ensure the summary is clear, detailed, and informative, reflecting the executive summary style found in news articles. Avoid using phrases that directly reference 'the script provides' to maintain a direct and objective tone.
"{text}"
SUMMARY:
"""
map_prompt_template = PromptTemplate(template=map_prompt, input_variables=["text"])

combine_prompt = """
Write a complete summary of the following text.
maintain a direct and objective tone.
"{text}"
SUMMARY:
"""
combine_prompt_template = PromptTemplate(template=combine_prompt, input_variables=["text"])

def segment_large_text(transcript, num_segments=4, overlap=20):

    part_size = len(transcript) // num_segments
    segments = [transcript[i: i + part_size] for i in range(0, len(transcript), part_size)]

    if len(segments) > num_segments:
        segments[-1] += ''.join(segments[num_segments:])
        del segments[num_segments:]

    return segments

def split_segment(segment):
    text_splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n"], chunk_size=4000, chunk_overlap=100)
    return text_splitter.create_documents([segment])

def summarize_segment(segment_docs, llm):
    summary_chain = load_summarize_chain(llm=llm,
                                         chain_type='map_reduce',
                                         map_prompt=map_prompt_template,
                                         combine_prompt=combine_prompt_template,
                                        )
    return summary_chain.run(segment_docs)
