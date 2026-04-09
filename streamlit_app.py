import streamlit as st

# ==================== 1. 網頁基本設定與全域 CSS 美化 ====================
st.set_page_config(layout="wide", page_title="AI 圖片提示詞生成器")

# 注入自定義 CSS 美化介面
custom_css = """
<style>
    /* 隱藏預設的選單與底部浮水印 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 替換整體背景為高級暗色漸層 */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #09090b 50%, #1e1b4b 100%);
        background-attachment: fixed;
        color: #f8fafc;
    }

    /* 確保原本預設的白色/黑色底色透明化，讓漸層透出來 */
    [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: transparent !important;
    }
    
    /* 漸層大標題 */
    .main-title {
        background: linear-gradient(135deg, #818cf8 0%, #f472b6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem !important;
        font-weight: 900 !important;
        margin-bottom: 0px !important;
        padding-bottom: 10px;
    }
    
    /* 副標題與敘述小字 */
    .sub-title {
        font-size: 1.1rem;
        color: #9ca3af;
        margin-bottom: 2rem;
        font-weight: 500;
    }

    /* 區塊標題 (帶有左側色塊裝飾) */
    .section-header {
        font-size: 1.4rem;
        font-weight: 700;
        color: #f3f4f6;
        margin-top: 2.5rem;
        margin-bottom: 1rem;
        padding-left: 12px;
        border-left: 6px solid #4F46E5;
        letter-spacing: 0.5px;
    }

    /* 所有 Alert 框 (Info, Warning, Error) 增加大圓角與微透明 */
    [data-testid="stAlert"] {
        border-radius: 12px;
        border: none;
        background-color: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        color: #e5e7eb;
    }

    /* 輸入框與下拉選單的圓角與預設顏色 */
    .stTextInput input, .stNumberInput input, div[data-baseweb="select"] > div {
        border-radius: 10px !important;
        background-color: rgba(0, 0, 0, 0.2) !important;
        color: #f3f4f6 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    /* ⭐ 強化被鎖定 (Disabled) 元件的視覺效果 */
    [data-testid="stDisabled"] {
        opacity: 0.6 !important;
        cursor: not-allowed !important;
    }
    [data-testid="stDisabled"] * {
        cursor: not-allowed !important;
    }

    /* ⭐ 強制將被鎖定的輸入框與下拉選單內的文字變成明顯的灰色 */
    [data-testid="stDisabled"] div[data-baseweb="select"] > div,
    [data-testid="stDisabled"] div[data-baseweb="select"] span,[data-testid="stDisabled"] .stTextInput input,
    [data-testid="stDisabled"] .stNumberInput input {
        color: #6b7280 !important; /* 深灰色 */
        -webkit-text-fill-color: #6b7280 !important; /* 確保瀏覽器強制覆寫顏色 */
        background-color: rgba(0, 0, 0, 0.4) !important; /* 背景變得更暗 */
    }

    /* 主要按鈕美化 (漸層 + 動畫) */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-size: 1.2rem;
        font-weight: bold;
        letter-spacing: 1px;
        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.3);
        transition: all 0.3s ease;
        width: 100%;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(79, 70, 229, 0.5);
    }
    
    /* 模式選擇 (Radio Button) 加上背景框使其像開關 */
    div.row-widget.stRadio > div {
        background-color: rgba(255, 255, 255, 0.03);
        padding: 15px 20px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* 雷達圖卡片美化 */
    .radar-card {
        background: linear-gradient(145deg, rgba(79,70,229,0.1) 0%, rgba(236,72,153,0.05) 100%);
        border: 1px solid rgba(255,255,255,0.05);
        padding: 15px; 
        border-radius: 16px; 
        text-align: center; 
        font-size: 22px; 
        line-height: 1.6; 
        letter-spacing: 4px; 
        margin-bottom: 5px;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
        backdrop-filter: blur(5px);
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==================== 2. 簡易密碼鎖設定 ====================
TEAM_PASSWORD = "52654260" 

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h1 class='main-title'>登入以繼續</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>請輸入團隊專屬的通關密碼</p>", unsafe_allow_html=True)
    pwd_input = st.text_input("密碼", type="password", label_visibility="collapsed", placeholder="輸入密碼後按 Enter")
    if pwd_input == TEAM_PASSWORD:
        st.session_state.authenticated = True
        st.rerun()
    elif pwd_input != "":
        st.error("密碼錯誤，請重新輸入！")
    st.stop()

# ==================== 3. 字典定義區 ====================
base_negative = "ugly, deformed, blurry, poor details, bad anatomy, worst quality, low quality, jpeg artifacts, overexposed, underexposed"

dict_style = {
    "寫實商業攝影": "clean commercial photography, natural high-end realism, soft cinematic realism, muted saturation, balanced dynamic range, smooth highlight roll-off, gentle tonal separation, delicate midtone detail, subtle film grain, organic tonal response, crisp but not overly sharpened, refined texture clarity, smooth tonal gradation", 
    "高級精品感": "high-end luxury, editorial fashion photography, sleek, sophisticated", 
    "科技未來感": "cyberpunk, sci-fi, futuristic, glowing neon lights, intricate mechanical details", 
    "溫暖生活感": "warm lifestyle, slice of life, cozy atmosphere, candid photography", 
    "年輕潮流感": "trendy streetwear, youth culture, dynamic, vibrant colors", 
    "日系清透": "Japanese aesthetic, clear and airy, muted pastel colors, soft focus, film photography", 
    "歐美廣告劇照": "cinematic still, Hollywood movie aesthetic, dramatic lighting, 35mm photograph", 
    "插畫風": "digital illustration, vibrant colors, flat design, vector art, 2D", 
    "3D 視覺風": "3D render, octane render, unreal engine 5, path tracing, volumetric lighting"
}

dict_shot = {"極特寫": "extreme close-up", "特寫": "close-up", "半身": "medium shot, waist up", "膝上景": "cowboy shot", "全身景": "full body", "遠景": "wide shot, wide angle", "超大遠景": "extreme wide shot, extreme long shot, establishing shot, tiny subject"}

dict_angle = {
    "平視 (Eye Level)": "eye-level angle, straight-on", 
    "仰視 (Low Angle - 攝影機在下)": "low angle shot, shot from below, camera pointing upward", 
    "俯視 (High Angle - 攝影機在上)": "high angle shot, shot from above, downward angle", 
    "傾斜荷蘭角 (Dutch Angle)": "dutch angle, tilted frame"
}

dict_position = {
    "正前方拍攝": "front view, camera placed straight ahead",
    "左前方拍攝": "front-left view, camera placed front-left",
    "右前方拍攝": "front-right view, camera placed front-right",
    "正左側拍攝": "left profile view, exact left side view",
    "正右側拍攝": "right profile view, exact right side view",
    "左後方拍攝": "back-left view, camera placed behind left shoulder",
    "右後方拍攝": "back-right view, camera placed behind right shoulder",
    "正後方拍攝": "back view, exact shot from behind",
    "過肩鏡頭 (Over the shoulder)": "over the shoulder shot, OTS",
    "第一人稱視角 (POV)": "first-person view, POV, seeing through eyes"
}

dict_position_map = {
    "正前方拍攝": "▫️ ▫️ ▫️<br>▫️ 👤 ▫️<br>▫️ 📷 ▫️",
    "左前方拍攝": "▫️ ▫️ ▫️<br>▫️ 👤 ▫️<br>📷 ▫️ ▫️",
    "右前方拍攝": "▫️ ▫️ ▫️<br>▫️ 👤 ▫️<br>▫️ ▫️ 📷",
    "正左側拍攝": "▫️ ▫️ ▫️<br>📷 👤 ▫️<br>▫️ ▫️ ▫️",
    "正右側拍攝": "▫️ ▫️ ▫️<br>▫️ 👤 📷<br>▫️ ▫️ ▫️",
    "左後方拍攝": "📷 ▫️ ▫️<br>▫️ 👤 ▫️<br>▫️ ▫️ ▫️",
    "右後方拍攝": "▫️ ▫️ 📷<br>▫️ 👤 ▫️<br>▫️ ▫️ ▫️",
    "正後方拍攝": "▫️ 📷 ▫️<br>▫️ 👤 ▫️<br>▫️ ▫️ ▫️",
    "過肩鏡頭 (Over the shoulder)": "▫️ ▫️ ▫️<br>▫️ 👤 ▫️<br>▫️ 📷 👤",
    "第一人稱視角 (POV)": "▫️ ▫️ ▫️<br>▫️ 👀 ▫️<br>▫️ ▫️ ▫️"
}

dict_light = {
    "白天自然光": "natural light, sunlight", 
    "黃昏日落暖光 (Magic hour)": "golden hour, sunset lighting", 
    "夜晚": "night, ambient lighting", 
    "棚拍柔光": "soft diffused light, even illumination, flawless lighting, gentle shadows", 
    "高反差戲劇光": "dramatic lighting, high contrast", 
    "冷色科技光": "cool tone, blue and teal lighting"
}

dict_ratio = {
    "橫式簡報滿版 (16:9)": "16:9 aspect ratio, landscape", 
    "IG限動 (9:16)": "9:16 aspect ratio, portrait", 
    "方形 (1:1)": "1:1 aspect ratio, square",
    "傳統橫式 (4:3)": "4:3 aspect ratio, landscape",
    "社群直式 (3:4)": "3:4 aspect ratio, portrait",
    "電影寬螢幕 (21:9)": "21:9 aspect ratio, ultrawide, cinematic"
}

# ==================== 4. UI 介面設計 ====================

st.markdown("<h1 class='main-title'>AI 圖片提示詞生成器</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>精準控制畫面分鏡，專為 Nano Banana 2 引擎打造。</p>", unsafe_allow_html=True)

# --- 【全新模式切換器】 ---
st.markdown("<div class='section-header'>選擇產圖模式</div>", unsafe_allow_html=True)
mode = st.radio(
    "模式選擇",["一般生成模式 (從零開始)", "畫面重構模式 (換動作/換視角)", "分鏡保留模式 (換人/換場景)"],
    horizontal=True,
    label_visibility="collapsed"
)

is_remake_mode = mode == "畫面重構模式 (換動作/換視角)"
is_layout_mode = mode == "分鏡保留模式 (換人/換場景)"
is_normal_mode = mode == "一般生成模式 (從零開始)"

if is_normal_mode:
    st.info("**一般生成模式**：不需參考圖，直接透過文字指令生成全新的畫面。")
elif is_remake_mode:
    st.info("**畫面重構模式**：繼承參考圖 [Image 1] 的主角外貌與光影。您可以修改動作、場景，並強制更改鏡頭視角。")
elif is_layout_mode:
    st.info("**分鏡保留模式**：鎖定參考圖[Image 1] 的所有攝影機位置與構圖。您可以將畫面的主角、動作、背景或光線換掉。")


# --- 【第一區：核心內容】 ---
st.markdown("<div class='section-header'>畫面核心內容 (Who, Doing What, Where)</div>", unsafe_allow_html=True)
col_text1, col_text2, col_text3 = st.columns(3)

with col_text1:
    if is_remake_mode:
        subj_label = "畫面主角 (Who) 🔒 [重構模式已鎖定]"
        subj_val = "同主參考圖主角"
        subj_disabled = True
    else:
        subj_label = "畫面主角 (Who)"
        subj_val = "" if is_layout_mode else "一位穿白襯衫的年輕台灣女性"
        subj_disabled = False
        
    subj_help = "若留白，將維持參考圖原本的主角" if is_layout_mode else "*必填"
    user_keyword = st.text_input(subj_label, value=subj_val, disabled=subj_disabled, help=subj_help, placeholder="例如: 一位台灣男性")

with col_text2:
    act_help = "若留白，將維持原動作與姿勢" if (is_remake_mode or is_layout_mode) else "(可在此定義面向與表情) 非必填"
    user_action = st.text_input(
        "主角動作 (Doing What)", 
        value="" if (is_remake_mode or is_layout_mode) else "看向窗外，手裡拿著咖啡，神情放鬆", 
        placeholder="例如：看向窗外，手裡拿著咖啡，燦爛微笑", 
        help=act_help
    )

with col_text3:
    bg_help = "若留白，將維持原場景" if (is_remake_mode or is_layout_mode) else "*必填"
    bg_value = "" if (is_remake_mode or is_layout_mode) else "陽光明媚的現代咖啡廳"
    user_background = st.text_input("背景場景 (Where)", value=bg_value, placeholder="例如: 夜晚的東京街頭", help=bg_help)


# --- 【第二區：參考圖數量對應與連動】 ---
st.markdown("<div class='section-header'>參考圖片參數設定</div>", unsafe_allow_html=True)

st.info(
    "**【最佳參考圖規範】** 為了獲得最好的 AI 生成效果，請確保上傳的圖片符合以下條件：\n"
    "1. **高畫質且清晰**，主體佔比明確。\n"
    "2. **背景不要太複雜**，乾淨的背景能讓 AI 更容易抓取主角與物件。\n"
    "3. 絕對**不能有浮水印或壓字**，否則浮水印會被 AI 學習並出現在生成結果中。"
)

if is_normal_mode:
    st.warning("**排序提醒：** 請依照下方 **「人物 ➔ 物件 ➔ 光線」的順序上傳**，否則 [Image X] 的編號會對不起來！")
else:
    st.warning("**排序提醒：** 模式已鎖定第一張為主圖。上傳順序必須是 **主參考圖(必為第1張) ➔ 人物(若有) ➔ 物件(若有) ➔ 光線(若有)**。")

img_counter = 2 if not is_normal_mode else 1 
ref_prompts =[] 
custom_light_prompt = ""
use_light_ref = False
is_also_style_ref = False 

col_ref1, col_ref2, col_ref3 = st.columns(3)

with col_ref1:
    use_char_ref = st.checkbox("啟用人物參考圖")
    if use_char_ref:
        char_count = st.number_input("輸入人物參考圖數量", min_value=1, max_value=10, value=1, step=1)
        char_parts = st.multiselect("請選擇要參考的部位 (可複選)",["臉部特徵 (Face)", "服裝穿搭 (Clothing)", "眼鏡 (Glasses)", "帽子 (Hat)"])
        custom_parts = st.text_input("自定義參考部位 (選填)", placeholder="例如: 手錶 項鍊 (請用空白鍵隔開)", help="將會自動轉成英文標籤")
        
        char_labels = [f"[Image {i}]" for i in range(img_counter, img_counter + char_count)]
        img_counter += char_count 
        
        parts_map = {"臉部特徵 (Face)": "face", "服裝穿搭 (Clothing)": "clothing", "眼鏡 (Glasses)": "glasses", "帽子 (Hat)": "hat"}
        selected_parts =[parts_map[p] for p in char_parts]
        
        if custom_parts.strip() != "":
            custom_list =[word.strip() for word in custom_parts.replace(',', ' ').split() if word.strip()]
            selected_parts.extend(custom_list)
            
        parts_str = f" for {' and '.join(selected_parts)}" if selected_parts else ""
        joined_char_labels = " and ".join(char_labels)
        ref_prompts.append(f"referencing character details from {joined_char_labels}{parts_str}")

with col_ref2:
    use_obj_ref = st.checkbox("啟用物件參考圖")
    if use_obj_ref:
        obj_count = st.number_input("輸入物件參考圖數量", min_value=1, max_value=10, value=1, step=1)
        obj_attr = st.text_input("請描述物件屬性 (填空)", placeholder="例如：紅色的皮革包包")
        obj_labels =[f"[Image {i}]" for i in range(img_counter, img_counter + obj_count)]
        img_counter += obj_count 
        attr_str = f" as {obj_attr}" if obj_attr else ""
        
        joined_obj_labels = " and ".join(obj_labels)
        ref_prompts.append(f"referencing object {joined_obj_labels}{attr_str}")

with col_ref3:
    if is_remake_mode:
        st.checkbox("光線與色調參考圖 🔒 [重構模式已鎖定]", value=False, disabled=True)
    else:
        use_light_ref = st.checkbox("啟用光線與色調參考圖", help="若使用「真實照片」作為光線參考，生成的逼真度與質感效果會最佳！")
        if use_light_ref:
            light_count = st.number_input("輸入光線參考圖數量", min_value=1, max_value=10, value=1, step=1)
            is_also_style_ref = st.checkbox("同時作為「視覺風格」參考圖")
            
            info_msg = f"鎖定「光線與色調」選單，並佔用 {light_count} 個 Image 編號。"
            if is_also_style_ref:
                info_msg = f"鎖定「視覺風格」與「光線」選單，佔用 {light_count} 個 Image 編號。"
            st.info(info_msg)
            
            light_labels = [f"[Image {i}]" for i in range(img_counter, img_counter + light_count)]
            img_counter += light_count 
            
            joined_light_labels = " and ".join(light_labels)
            if is_also_style_ref:
                custom_light_prompt = f"matching the exact visual style, lighting, color grading, and texture of {joined_light_labels}"
            else:
                custom_light_prompt = f"matching the exact lighting, color grading, and texture of {joined_light_labels}"


# --- 【第三區：攝影與風格控制】 ---
st.markdown("<div class='section-header'>攝影與風格控制</div>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

camera_disabled = is_layout_mode

with col1:
    style_label = "視覺風格 🔒 [由參考圖決定]" if (is_remake_mode or is_also_style_ref) else "視覺風格"
    style_choice = st.selectbox(
        style_label, 
        ["維持原圖風格"] + list(dict_style.keys()) if is_layout_mode else list(dict_style.keys()), 
        disabled=is_remake_mode or is_also_style_ref
    )
    
    light_label = "光線與色調 🔒 [由參考圖決定]" if (use_light_ref or is_remake_mode) else "光線與色調"
    light_choice = st.selectbox(
        light_label,
        ["維持原圖光影"] + list(dict_light.keys()) if is_layout_mode else list(dict_light.keys()), 
        disabled=use_light_ref or is_remake_mode
    )

with col2:
    shot_label = "鏡頭大小 🔒 [分鏡已鎖定]" if camera_disabled else "鏡頭大小"
    shot_choice = st.selectbox(shot_label, list(dict_shot.keys()), disabled=camera_disabled)
    
    angle_label = "鏡頭角度 🔒 [分鏡已鎖定]" if camera_disabled else "鏡頭角度"
    angle_choice = st.selectbox(angle_label, list(dict_angle.keys()), disabled=camera_disabled)

with col3:
    pos_label = "鏡頭位置 🔒[分鏡已鎖定]" if camera_disabled else "鏡頭位置"
    position_choice = st.selectbox(pos_label, list(dict_position.keys()), disabled=camera_disabled)
    
    if not camera_disabled:
        st.markdown("**鏡頭位置示意圖：**")
        radar_html = dict_position_map[position_choice]
        st.markdown(f"""
            <div class='radar-card'>
                {radar_html}
            </div>
        """, unsafe_allow_html=True)
        st.caption("*( 人像下方為正前方 )*")
    
    ratio_choice = st.selectbox("畫面比例", list(dict_ratio.keys()))
    append_ratio = st.checkbox("將比例標籤加入提示詞結尾", value=False)


# --- 【第四區：負面提示詞】 ---
st.markdown("<div class='section-header'>負面提示詞 (Negative Prompt) - 選填</div>", unsafe_allow_html=True)
user_negative = st.text_input(
    "想要排除的額外元素 (請用「空白鍵」隔開不同的詞)", 
    placeholder="例如: text logo watermark ugly trees"
)

st.markdown("<br>", unsafe_allow_html=True)

# ==================== 5. 產圖邏輯區與衝突檢測 ====================

conflicts =[]

if not camera_disabled:
    if "POV" in position_choice:
        conflicts.append("**視角衝突**：選擇了「第一人稱視角 (POV)」，通常會看不到主角本人。")
    face_keywords =["笑", "看", "眼", "嘴", "表情", "臉", "盯"]
    if ("後方" in position_choice) and any(word in user_action for word in face_keywords):
        conflicts.append("**面向衝突**：背後視角與臉部表情描述衝突。")
    if shot_choice == "極特寫" and "過肩鏡頭" in position_choice:
        conflicts.append("**鏡頭衝突**：「極特寫」無法容納「過肩鏡頭」所需的前景。")

bg_lower = user_background.lower()
night_keywords =["夜", "night", "晚", "星空"]
day_keywords =["白", "日", "早", "陽光", "sun", "day", "morning", "afternoon"]

if is_normal_mode and not use_light_ref:
    if light_choice == "白天自然光" and any(word in bg_lower for word in night_keywords):
        conflicts.append("**光影衝突**：光線選擇白天，但背景描述為夜晚。")
    elif light_choice == "夜晚" and any(word in bg_lower for word in day_keywords):
        conflicts.append("**光影衝突**：光線選擇夜晚，但背景描述包含白天/陽光。")

if conflicts:
    st.error("**提示詞衝突警告 (請檢視下方問題，以免生成失敗)：**")
    for msg in conflicts:
        st.warning(msg)

if st.button("組合生成咒語 (Generate Prompt)", type="primary", use_container_width=True):
    
    if is_normal_mode and (user_keyword.strip() == "" or user_background.strip() == ""):
        st.error("一般模式下，請確實填寫「畫面主角」與「背景場景」！")
    else:
        custom_neg_tags = ""
        if user_negative.strip() != "":
            word_list =[word.strip() for word in user_negative.replace(',', ' ').split() if word.strip()]
            custom_neg_tags = ", ".join(word_list)

        if is_remake_mode:
            base_prompt = "maintaining the exact subject, visual style, color grading and lighting of[Image 1]"
            
            if user_action.strip():
                base_prompt += f", changing action to: {user_action.strip()}"
            else:
                base_prompt += ", maintaining the exact pose and posture of[Image 1]"
                
            if user_background.strip():
                base_prompt += f", changing background to: {user_background.strip()}"
                
            base_prompt += f", moving camera view to: {dict_shot[shot_choice]}, {dict_angle[angle_choice]}, {dict_position[position_choice]}"
            final_prompt = base_prompt + ", " + ", ".join(ref_prompts) if ref_prompts else base_prompt

        elif is_layout_mode:
            base_prompt = "maintaining the exact camera angle, shot size, and composition of [Image 1]"
            
            if user_keyword.strip():
                base_prompt += f", changing subject to: {user_keyword.strip()}"
            else:
                base_prompt += ", maintaining the exact subject of[Image 1]"
                
            if user_action.strip():
                base_prompt += f", changing action to: {user_action.strip()}"
            else:
                base_prompt += ", maintaining the exact pose and posture of [Image 1]"
                
            if user_background.strip():
                base_prompt += f", changing background to: {user_background.strip()}"
            
            if style_choice != "維持原圖風格" and not is_also_style_ref:
                base_prompt += f", changing style to: {dict_style[style_choice]}"
            
            if use_light_ref:
                base_prompt += f", {custom_light_prompt}"
            elif light_choice != "維持原圖光影":
                base_prompt += f", changing lighting to: {dict_light[light_choice]}"

            final_prompt = base_prompt + ", " + ", ".join(ref_prompts) if ref_prompts else base_prompt

        else:
            subject_and_action = f"{user_keyword}, {user_action}" if user_action.strip() else f"{user_keyword}"
            final_light = custom_light_prompt if use_light_ref else dict_light[light_choice]
            final_style = "" if is_also_style_ref else f"{dict_style[style_choice]}, "

            base_prompt = (
                f"{subject_and_action}, "
                f"in {user_background}, "
                f"{dict_shot[shot_choice]}, "
                f"{dict_angle[angle_choice]}, "
                f"{dict_position[position_choice]}, "
                f"{final_style}"
                f"{final_light}"
            )
            final_prompt = base_prompt + ", " + ", ".join(ref_prompts) if ref_prompts else base_prompt

        if append_ratio:
            final_prompt += f", {dict_ratio[ratio_choice]}"

        st.success("成功生成提示詞！請點擊右上方按鈕一鍵複製。")
        st.markdown("**請將滑鼠移至下方黑框的右上角，點擊出現的複製圖示即可一鍵全選複製**")
        
        if custom_neg_tags:
            combined_output = f"{final_prompt}\n\n[Negative Prompt]\n{custom_neg_tags}"
        else:
            combined_output = f"{final_prompt}"
            
        st.code(combined_output, language="text")
        
        st.info(f"**【尺寸參數設定建議】** 寬度：`{1920 if '16:9' in ratio_choice else (1080 if '9:16' in ratio_choice else (1024 if '1:1' in ratio_choice else (1440 if '4:3' in ratio_choice else (1080 if '3:4' in ratio_choice else 2560))))}`px ｜ 高度：`{1080 if '16:9' in ratio_choice else (1920 if '9:16' in ratio_choice else (1024 if '1:1' in ratio_choice else (1080 if '4:3' in ratio_choice else (1440 if '3:4' in ratio_choice else 1080))))}`px")