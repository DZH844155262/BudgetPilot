from functools import lru_cache
from typing import Sequence

import numpy as np
from sentence_transformers import SentenceTransformer


MODEL_NAME = "BAAI/bge-small-zh-v1.5"

QUERY_INSTRUCTION = (
    "为这个句子生成表示以用于检索相关文章："
)


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """加载并缓存中文 Embedding 模型。"""

    return SentenceTransformer(MODEL_NAME)


def get_embedding_dimension() -> int:
    """返回模型生成的向量维度。"""

    dimension = (
        get_embedding_model()
        .get_embedding_dimension()
    )

    if dimension is None:
        raise RuntimeError("无法获取 Embedding 向量维度")

    return dimension


def embed_documents(
    texts: Sequence[str],
) -> list[list[float]]:
    """为制度文档块生成向量。"""

    cleaned_texts = [
        text.strip()
        for text in texts
    ]

    if not cleaned_texts:
        raise ValueError("文档列表不能为空")

    if any(not text for text in cleaned_texts):
        raise ValueError("文档内容不能为空")

    vectors = get_embedding_model().encode(
        cleaned_texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )

    return vectors.tolist()


def embed_query(
    query: str,
) -> list[float]:
    """为用户检索问题生成向量。"""

    cleaned_query = query.strip()

    if not cleaned_query:
        raise ValueError("查询内容不能为空")

    instructed_query = (
        f"{QUERY_INSTRUCTION}{cleaned_query}"
    )

    vector = get_embedding_model().encode(
        instructed_query,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )

    return vector.tolist()


def cosine_similarity(
    vector_a: Sequence[float],
    vector_b: Sequence[float],
) -> float:
    """计算两个已归一化向量的余弦相似度。"""

    array_a = np.asarray(
        vector_a,
        dtype=np.float32,
    )
    array_b = np.asarray(
        vector_b,
        dtype=np.float32,
    )

    if array_a.shape != array_b.shape:
        raise ValueError("两个向量维度必须一致")

    return float(np.dot(array_a, array_b))


if __name__ == "__main__":
    query = "单笔费用达到20000元需要谁复核？"

    documents = [
        "单笔费用达到20000元时，应提交部门负责人和财务人员复核。",
        "软件自动续费前应进行必要性评估。",
    ]

    query_vector = embed_query(query)
    document_vectors = embed_documents(documents)

    print(f"模型：{MODEL_NAME}")
    print(f"向量维度：{get_embedding_dimension()}")

    for document, vector in zip(
        documents,
        document_vectors,
        strict=True,
    ):
        score = cosine_similarity(
            query_vector,
            vector,
        )

        print(f"\n相似度：{score:.4f}")
        print(f"文本：{document}")