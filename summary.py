from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate

class MapReduceDocSummarizer:
    def __init__(self, llm):
        self.llm = llm

        # Define the summarization prompts
        map_prompt = """
        Write a concise summary of the following:
        "{text}"
        SUMMARY:
        """
        self.map_prompt_template = PromptTemplate(template=map_prompt, input_variables=["text"])
        combine_prompt = """
        Write a concise summary of the following text delimited by triple backquotes.
        Return your response in bullet points which covers the key points of the text.
        ```{text}```
        BULLET POINT SUMMARY:
        """
        self.combine_prompt_template = PromptTemplate(template=combine_prompt, input_variables=["text"])

    def split_segment(self, doc, chunk_size=10000, chunk_overlap=500):
        text_splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n"], chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        return text_splitter.create_documents([doc])

    def summarize_segment(self, docs):
        summary_chain = load_summarize_chain(llm=self.llm,
                                             chain_type='map_reduce',
                                             map_prompt=self.map_prompt_template,
                                             combine_prompt=self.combine_prompt_template)
        return summary_chain.invoke(docs)

    def summary(self, doc, chunk_size=10000, chunk_overlap=500):
        segmented = self.split_segment(doc, chunk_size, chunk_overlap)
        summarized = self.summarize_segment(segmented)
        return summarized
