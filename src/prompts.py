from langchain.prompts import PromptTemplate

def get_summary_prompt(max_length: int) -> PromptTemplate:
    """
    Returns a PromptTemplate for summarizing text.

    Args:
        max_length (int): Maximum length of the summary.

    Returns:
        PromptTemplate: A LangChain PromptTemplate instance.
    """
    template = f"""
    Provide a concise summary of the following text in no more than {max_length} characters. 
    Do not include any introductory phrases or headings.

    {{document}}
    """
    return PromptTemplate(template=template, input_variables=["document"])