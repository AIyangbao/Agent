from rag.retrieve import should_retrieve

def test_chitchat_blocked():
    assert should_retrieve("你好") is False
    assert should_retrieve("谢谢!") is False
    assert should_retrieve("hello") is False

def test_real_question_passes():
    assert should_retrieve("你好, 帮我总结下 Docker 那篇") is True
    assert should_retrieve("Redis 防击穿怎么做的") is True
    assert should_retrieve("Vue") is True