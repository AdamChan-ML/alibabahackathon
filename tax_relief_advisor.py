import os
from http import HTTPStatus
from dashscope import Application
import dashscope
from datetime import datetime

# Configure DashScope
dashscope.base_http_api_url = 'https://dashscope-intl.aliyuncs.com/api/v1'

def get_tax_summary():
    """Get a brief summary of tax relief analysis"""
    expenses = {
        "Automatic individual relief": 9000,
        "Medical expenses for parents": 8000,
        "Education fees in Malaysia": 5000
    }

    prompt = f"""Based on these Malaysian tax expenses for year {datetime.now().year}:
1. Automatic individual relief: RM {expenses['Automatic individual relief']}
2. Medical expenses for parents: RM {expenses['Medical expenses for parents']}
3. Education fees in Malaysia: RM {expenses['Education fees in Malaysia']}

Provide a BRIEF summary (max 5 bullet points) of key tax relief insights, focusing on:
- Current utilization status
- Key opportunities
- Important recommendations
- Any unused relief categories that could be beneficial
- Next steps"""

    try:
        response = Application.call(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            app_id='f15e6f2c3b56437bac6d0afe9b018f02',
            prompt=prompt,
            rag_options={
                "knowledge_base_ids": ["r94ym9j3g7"],
                "top_k": 5,
                "similarity_threshold": 0.7,
                "return_source": True
            }
        )

        if response.status_code == HTTPStatus.OK:
            return response.output.text, None
        else:
            error_msg = f"Error: API call failed (Status: {response.status_code}, Message: {response.message})"
            return None, error_msg

    except Exception as e:
        return None, str(e)

def chat_with_context(user_input, session_id=None):
    """Chat with the AI while maintaining tax context"""
    try:
        # If no session_id, start a new conversation with context
        if not session_id:
            context = """Current Malaysian tax expenses context:
- Automatic individual relief: RM 9,000
- Medical expenses for parents: RM 8,000
- Education fees in Malaysia: RM 5,000

Please provide tax-related advice based on this context."""
            
            response = Application.call(
                api_key=os.getenv("DASHSCOPE_API_KEY"),
                app_id='f15e6f2c3b56437bac6d0afe9b018f02',
                prompt=f"{context}\n\nUser question: {user_input}",
                rag_options={
                    "knowledge_base_ids": ["r94ym9j3g7"],
                    "top_k": 5,
                    "similarity_threshold": 0.7,
                    "return_source": True
                }
            )
        else:
            # Continue existing conversation
            response = Application.call(
                api_key=os.getenv("DASHSCOPE_API_KEY"),
                app_id='f15e6f2c3b56437bac6d0afe9b018f02',
                prompt=user_input,
                session_id=session_id,
                rag_options={
                    "knowledge_base_ids": ["r94ym9j3g7"],
                    "top_k": 5,
                    "similarity_threshold": 0.7,
                    "return_source": True
                }
            )

        if response.status_code == HTTPStatus.OK:
            return response.output.text, response.output.session_id, None
        else:
            error_msg = f"Error: API call failed (Status: {response.status_code}, Message: {response.message})"
            return None, None, error_msg

    except Exception as e:
        return None, None, str(e)

if __name__ == "__main__":
    # Test summary
    summary, error = get_tax_summary()
    if summary:
        print("=== Tax Relief Summary ===")
        print(summary)
    else:
        print(f"Error getting summary: {error}")

    # Test chat
    print("\n=== Interactive Chat ===")
    response, session_id, error = chat_with_context("What documents do I need for medical expense claims?")
    if response:
        print(f"Response: {response}")
        print(f"Session ID: {session_id}")
    else:
        print(f"Error in chat: {error}") 