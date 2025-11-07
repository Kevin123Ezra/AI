import streamlit as st
from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

st.title("AI Summarizer App")
st.divider()

st.markdown("## Start summarizing your documents with AI!")

uploading_file = st.file_uploader("Upload a text, pdf or docx file", type=["pdf", "txt", "docx"])

llm = ChatGroq(model="llama-3.1-8b-instant")

parser = StrOutputParser()

prompt_template = ChatPromptTemplate.from_template("Summarize the following document: {document}")

#chain = prompt_template | llm | parser 

if uploading_file is not None:
    with st.spinner("Processing..."):
        try:
            temp_file_path = uploading_file.name

            print("File name:", uploading_file)
            print("File path:", temp_file_path)
            print("File type:", uploading_file.type)
            print("File size:", uploading_file.size)

            with open(temp_file_path, "wb") as f:
                f.write(uploading_file.getbuffer())
            
            if uploading_file.type == "application/pdf":
                loader = PyPDFLoader(temp_file_path)
                
            elif uploading_file.type == "text/plain":
                loader = TextLoader(temp_file_path)

            elif uploading_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                loader = Docx2txtLoader(temp_file_path)

            else:
                st.error("Unsupported file type!")
                st.stop()
            
            # loader
            documents = loader.load() 
            print(documents)

            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            chunks = text_splitter.split_documents(documents)

        except Exception as e:
            st.error(f"Error processing file: {e}")
            st.stop()
    
    st.success("File uploaded successfully!")

if st.button("Generate Summary"):
    container = st.empty()
    chunk_summaries = []
    if uploading_file is None:
        st.error("Please upload a file first!")
        st.stop()
    
    with st.spinner("Generating summary..."):
        try:
            for chunk in chunks:
                chunk_prompt = ChatPromptTemplate.from_template("You are a highly skilled AI tasked with summarizing text, Please summariz the follwoing chunk of text (with respect to the previous chunk if any), Highlighting the most important points, without omiting any information: {document}")
                chunk_chain = chunk_prompt | llm | parser
                chunk_summary = chunk_chain.invoke({"document": chunk})
                chunk_summaries.append(chunk_summary)

        except Exception as e:
            st.error(f"Error generating summary: {e}")
            st.stop()
    
    with st.spinner("Creating final summary..."):
        try:
            combined_summaries = "\n".join(chunk_summaries)
            final_prompt = ChatPromptTemplate.from_template( "You are an expert summarizer tasked with creating a final summary from summarized chunks, Combine the key points from the provided summaries into a cohesive and comprehensive summary, The final summary should be concise but detailed enough to capture the main ideas:\n\n"
                "{document}")
            
            final_chain = final_prompt | llm | parser
            final_summary = final_chain.invoke({"document": combined_summaries})

            print("Final Summary:", final_summary)
            container.write(final_summary)

            st.download_button(label ="Download Summary", data=final_summary, file_name=f"Summary of {uploading_file.name}.txt", mime="text/plain")

        except Exception as e:
            st.error(f"Error creating final summary: {e}")
            st.stop()
