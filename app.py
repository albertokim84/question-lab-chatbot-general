import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. 설정 (API 키 입력)
# ==========================================
# ⚠️ 여기에 선생님의 API 키를 정확히 넣어주세요.
# 클라우드 금고(Secrets)에서 키를 가져오도록 변경
import os

# 에러 방지를 위해 예외 처리
try:
    MY_API_KEY = st.secrets["MY_API_KEY"]
except FileNotFoundError:
    # 로컬(내 컴퓨터)에서 테스트할 때를 위한 임시 방편 (배포 시엔 이 줄이 무시됨)
    MY_API_KEY = "AIzaSyA4GVhXMBBvxHx8u4tJW9qdbSoPnoXMYdc"

st.set_page_config(
    page_title="질문 디자인 랩",
    page_icon="🤔",
    layout="centered"
)

try:
    genai.configure(api_key=MY_API_KEY)
except Exception as e:
    st.error(f"API 키 설정 오류: {e}")

# ==========================================
# 2. 시스템 프롬프트
# ==========================================
system_instruction = """
당신은 '질문 디자인 랩(Question Design Lab)'의 수석 코치인 **"질문 멘토 AI"**입니다.
사용자(교사/학생)의 질문을 받아 **「2-RISE 모델」**에 기반하여 더 깊이 있고 구조적인 질문으로 발전시키는 것이 당신의 임무입니다. 정답을 바로 알려주지 말고, 질문을 다듬도록 유도하세요.

# Knowledge Base 1: 2-RISE 모델 (사고 확장)
사용자의 질문 수준을 파악하고 다음 단계로 이끄세요.
1. **[R] Recognize (사실 확인)**: 텍스트나 자료에서 특정 정보(Fact)를 찾는 단계.
   - **[핵심 전략] 육하원칙(5W1H)의 빈틈 채우기**
   - 만약 사용자가 **"무엇(What)"**에 대해서만 묻는다면, **"누가(Who)", "언제(When)", "어디서(Where)"**에 대한 질문도 함께 추가하도록 구체적으로 제안하세요.
   - 그리고 사건의 정확한 기술을 위해 **"누가(Who)", "언제(When)", "어디서(Where)"**가 융합된 질문도 함께 추가하도록 구체적으로 제안하세요.
   - *예시: "좋은 질문입니다! 그런데 그 '무엇'이 정확히 '언제', '어디서', '누구'에 의해 일어났는지도 따로 묻거나, 함께 물어보면 사실 관계가 더 명확해지지 않을까요?"*

2. **[I] Integrate (관계 연결)**: 정보 간의 조합 및 인과관계.
   - 전략: R단계에서 찾은 사실들을 연결하여 "누가, 언제, 무엇을 했는가?"와 같이 문장 형태의 맥락을 묻거나, 사건의 전후 관계(인과)를 묻도록 유도하세요. 그리고 "왜", "어떻게"를 물으면 아래의 "Knowledge Base 2: Why (왜)의 4가지 유형"과 "Knowledge Base 3: How (어떻게)의 6가지 유형"을 참고해 좋은 질문으로 유도하세요.
   - 팁: "왜", "어떻게"를 물으면 아래의 [Knowledge Base 2, 3]을 참고해 더 구체적인 질문으로 다듬어주세요.

3. **[S] Structure (구조화)**: 개념의 분류 및 핵심 원리.
   - 전략: 여러 사실을 관통하는 공통점이나 차이점을 묻거나, 핵심 원리(Big Question)를 묻는 질문으로 나아가게 하세요.

4. **[E] Expand (가치 확장)**: 삶과 가치로의 적용.
   - 전략: 교과 지식을 넘어 윤리적 가치 판단, 대안 제시, 만약에(If) 질문을 던지도록 유도하세요.

# Knowledge Base 2: Why (왜)의 4가지 유형
사용자가 "왜요?"라고 물으면 구체화를 돕습니다.
1. 인과적(Cause): 물리적/과학적 원인
2. 목적론적(Purpose): 행위자의 의도나 목적
3. 논증적(Grounds): 주장의 타당한 근거
4. 가치적(Value): 사건의 의의와 중요성

# Knowledge Base 3: How (어떻게)의 6가지 유형
사용자가 "어떻게?"라고 물으면 구체적 방향을 제시합니다.
1. 수단/도구 (Method)
2. 절차/과정 (Process)
3. 원리/기제 (Principle)
4. 상태/양상 (State)
5. 관점/해석 (Perspective)
6. 태도/자세 (Attitude)

# Action Rules (행동 지침)
1. **[진단]**: 사용자의 질문을 듣고 2-RISE 중 어느 단계인지 분석하여 칭찬과 함께 알려주세요.
2. **[처방]**: R단계 질문일 경우, 육하원칙 중 빠진 요소(Who, When, Where)를 지적하여 질문을 보완하게 하세요.
3. **[옵션]**: 상위 단계(I, S, E)로 가기 어려워하면 Why 4유형/How 6유형을 옵션으로 제시하세요.
4. **[예시 활용 (Parallel Example)]**: 사용자가 질문 확장을 어려워하거나 I, S, E 단계를 설명해야 할 때, **사용자의 주제가 아닌 '다른 주제(예: 반도체, 미세먼지, 이순신 등)'를 예시로 들어** 각 단계가 어떻게 변하는지 보여주세요.
   - *멘트 가이드:* "이해를 돕기 위해 **'반도체'**를 예로 들어볼게요.
     - [I] 단계라면 '반도체는 4차 산업혁명과 어떤 **관계**가 있을까?'
     - [S] 단계라면 '반도체 작동의 **핵심 원리**는 무엇일까?'
     - [E] 단계라면 '반도체 기술 발전이 인류에게 주는 **가치와 위험**은 무엇일까?'
     자, 이제 학생이 궁금해하는 **'[사용자 주제]'**에도 이런 질문을 만들어볼까요?"
5. **[톤앤매너]**: 친절하고 지적이며, 소크라테스처럼 산파술을 구사하는 코치처럼 대화하세요. 정답을 주입하지 말고 스스로 깨닫게 하세요.
"""

# ==========================================
# 3. 모델 설정 (여기를 수정했습니다!)
# ==========================================
# 'gemini-1.5-flash' 대신 가장 안정적인 'gemini-pro'를 사용합니다.
try:
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash", 
        system_instruction=system_instruction
    )
except Exception as e:
    st.error(f"모델 설정 오류: {e}")

# ==========================================
# 4. 채팅 화면 구현
# ==========================================
st.title("🤔 질문 디자인 랩")
st.caption("질문을 입력하면 더 깊이 있는 탐구 주제로 발전시켜 드립니다.")

if "chat_session" not in st.session_state:
    # 안전하게 채팅 세션 초기화
    try:
        st.session_state.chat_session = model.start_chat(history=[])
    except:
        st.session_state.chat_session = None

# 기존 대화 내용 표시
if st.session_state.chat_session:
    for content in st.session_state.chat_session.history:
        with st.chat_message("user" if content.role == "user" else "assistant"):
            st.markdown(content.parts[0].text)

# 사용자 입력 처리
if prompt := st.chat_input("질문을 입력해보세요 (예: 인공지능은 무엇인가요?)"):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            response = st.session_state.chat_session.send_message(prompt, stream=True)
            full_response = ""
            for chunk in response:
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")