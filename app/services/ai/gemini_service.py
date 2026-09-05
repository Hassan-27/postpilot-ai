from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Initialize the model once — reused across requests
llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=settings.GEMINI_API_KEY,
    temperature=0.7,       # 0 = deterministic, 1 = creative
    max_output_tokens=1024,
)

# The prompt template — this is the core of your AI product
linkedin_post_template = PromptTemplate(
    input_variables=["topic", "tone", "audience", "length"],
    template="""
You are an expert LinkedIn content writer who creates engaging, professional posts.

Write a LinkedIn post with the following specifications:
- Topic: {topic}
- Tone: {tone}
- Target Audience: {audience}
- Length: {length}

Requirements:
- Start with a strong hook that grabs attention
- Use short paragraphs for easy reading on mobile
- Include 3-5 relevant hashtags at the end
- Do not use generic openings like "In today's world" or "I am excited to share"
- Make it feel authentic, not like it was written by AI
- End with a clear call to action or thought-provoking question

Write only the post content, nothing else.
""",
)

# The chain — prompt → model → clean string output
post_generation_chain = linkedin_post_template | llm | StrOutputParser()


async def generate_linkedin_post(
    topic: str,
    tone: str = "professional",
    audience: str = "general professionals",
    length: str = "medium (150-200 words)",
) -> str:
    """Generate a LinkedIn post using LangChain + Gemini."""
    try:
        logger.info(f"Generating post for topic: {topic}")

        content = await post_generation_chain.ainvoke({
            "topic": topic,
            "tone": tone,
            "audience": audience,
            "length": length,
        })

        logger.info("Post generated successfully")
        return content.strip()

    except Exception as e:
        logger.error(f"Failed to generate post: {e}")
        raise ValueError(f"AI generation failed: {str(e)}")