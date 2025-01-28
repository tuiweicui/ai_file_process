import re
import logging
import spacy
from langdetect import detect, LangDetectException

# 配置日志
logging.basicConfig(level=logging.ERROR)

# 预加载模型
nlp_multi = spacy.load("xx_ent_wiki_sm")
nlp_en = spacy.load("en_core_web_sm")
nlp_zh = spacy.load("zh_core_web_sm")

def detect_language(text):
    try:
        return detect(text)
    except LangDetectException as e:
        logging.error(f"语言检测失败：{e}")
        raise e
    except Exception as e:
        logging.error(f"语言检测发生错误：{e}")
        raise e
def process_text(text: str) -> str:
    lang = detect(text)
    process_text=""
    if lang == "en":
        doc = nlp_en(text)
    elif lang == "zh":
        doc = nlp_zh(text)
    else:
        doc = nlp_multi(text)
    
    processed_tokens = [
        token.lemma_.lower()
        for token in doc
        if not token.is_stop and not token.is_punct
    ]
    if not processed_tokens:
        return text
    process_text = re.sub(r'\s+', ' ', process_text).strip()#使用正则表达式去除多余空格
    process_text=" ".join(processed_tokens).strip()
    return process_text
def parse_numbers(text):
    """
    try with string convert to number(integar/float)
    if no show in screen,return none
    """
    try:
        return int(text)
    except ValueError:
        try:
            if re.match(r'^\d+\.?\d*$',text):
                return float(text)
            else:
                logging.error(f"无法解析数字： {text}")
                return None
        except Exception as e:
            logging.error(f"尝试将使用模糊匹配数字发生错误： {e},无法解析为数字，{text}")
            return None
from langdetect import  DetectorFactory
# 初始化设置（解决随机性问题）
DetectorFactory.seed = 0

# 加载模型
nlp_en = spacy.load("en_core_web_sm")
nlp_zh = spacy.load("zh_core_web_sm")

def process_text(text):
    """更健壮的文本处理函数"""
    if not text.strip():
        return ""
    try:
        # 更可靠的语言检测
        lang = detect(text[:100])  # 检测前100字符足够
    except:
        lang = "en"  # 检测失败默认英语
    
    try:
        if lang in ["zh-cn", "zh-tw", "zh"]:
            doc = nlp_zh(text)
            tokens = [token.text for token in doc if not token.is_punct]
        else:
            doc = nlp_en(text)
            tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
            
        return " ".join(tokens).strip() if tokens else text[:100]  # 保底返回前100字符
    
    except Exception as e:
        logging.error(f"处理失败: {str(e)}")
        return None  # 失败时返回原始文本

def data_process(text):
    """更安全的预处理函数"""
    if text is None:
        return None#先进行None 输入判断然后进行后面的str判断。不然后面输入none导致代码结束
    try:
        # 处理None和空字符串
        if not text:
            return ""           
        # 基础清洗（保留大小写）
        text = re.sub(r'[\s\n]+', ' ', text).strip()
        return process_text(text) or text  # 双重保险
        
    except Exception as e:
        logging.error(f"预处理失败: {str(e)}")
        return text  # 保证始终返回字符串
def test_data_process():
    # 测试正常文本
    text1 = "This is a test sentence with some stopwords."
    expected1 = "test sentence stopword"
    assert data_process(text1) == expected1, f"Test case 1 failed, expect {expected1} but get {data_process(text1)}"
    # 测试包含大写字母的文本
    text2 = "This IS a Test sentence"
    expected2 = "test sentence"
    assert data_process(text2) == expected2, f"Test case 2 failed, expect {expected2} but get {data_process(text2)}"

    # 测试包含标点符号和换行符的文本
    text3 = "This is a test.\n sentence!"
    expected3 = "test sentence"
    assert data_process(text3) == expected3, f"Test case 3 failed, expect {expected3} but get {data_process(text3)}"

    # 测试不包含停用词的文本
    text4 = "Test sentence example"
    expected4 = "test sentence example"
    assert data_process(text4) == expected4, f"Test case 4 failed, expect {expected4} but get {data_process(text4)}"

    # 测试包含中文的文本
    text6="这是一个测试"
    expected6 = "这是 一个 测试"
    assert data_process(text6) == expected6, f"Test case 6 failed, expect {expected6} but get {data_process(text6)}"

    # 测试空字符串
    text7 = ""
    expected7 = ""
    assert data_process(text7) == expected7, f"Test case 7 failed, expect {expected7} but get {data_process(text7)}"
    # 测试None输入
    text8 = None
    assert data_process(text8) == None, f"Test case 8 failed, expect {None} but get {data_process(text8)}"

    print("All test cases passed!")
# 调用测试函数
test_data_process()