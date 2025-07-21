import chromadb
from chromadb.utils import embedding_functions
from config.settings import settings

class VectorDBClient:
    # def __init__(self):
    #     self.client = chromadb.PersistentClient(path=settings.VECTOR_DB_PATH)
    #     self.collection = self.client.get_or_create_collection(
    #         name="mbti_reactions",
    #         embedding_function=embedding_functions.DefaultEmbeddingFunction()
    #     )
    def __init__(self, mock_mode=True):
        self.mock_mode = mock_mode
        if not mock_mode:
            try:
                # 连接远程 Chroma
                self.client = chromadb.HttpClient(
                    host=settings.VECTOR_DB_HOST,
                    port=settings.VECTOR_DB_PORT,
                    ssl=False,  # 如果是 HTTPS 则改为 True
                    headers={
                        "Authorization": f"Bearer {settings.CHROMA_API_KEY}"  # 可选认证
                    } if settings.CHROMA_API_KEY else None
                )

                # 测试连接
                self.client.heartbeat()  # 发送心跳检测

                self.collection = self.client.get_or_create_collection(
                    name="mbti_reactions",
                    embedding_function=embedding_functions.DefaultEmbeddingFunction()
                )
                print("✅ 成功连接远程 Chroma 数据库")

            except Exception as e:
                print(f"❌ 连接 Chroma 失败: {str(e)}")
                raise

    def query_reactions(self, mbti: str, topic: str, top_k: int = 3) -> list[str]:
        """Query the vector DB for reactions related to MBTI and topic."""
        if self.mock_mode:
            print("⚠️ 向量数据库模拟模式：返回空数据")
            return []
        query_text = f"{mbti} reaction to {topic}"
        results = self.collection.query(
            query_texts=[query_text],
            n_results=top_k,
            include=["documents"]
        )
        return results.get("documents", [[]])[0] if results else []

# Instance for easy access
vector_db = VectorDBClient()

def retrieve_reactions(mbti: str, topic: str) -> str:
    """Hook to retrieve and format reactions from vector DB."""
    reactions = vector_db.query_reactions(mbti, topic)
    if not reactions:
        return ""
    return "\nRelevant reactions from database:\n" + "\n".join(reactions) 