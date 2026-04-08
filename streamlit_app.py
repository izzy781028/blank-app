import streamlit as st

# ==================== 1. 網頁基本設定 ====================
st.set_page_config(layout="wide", page_title="AI 圖片提示詞生成器")

# ==================== 2. 簡易密碼鎖設定 ====================
TEAM_PASSWORD = "52654260" 

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 內部測試工具：請輸入通關密碼")
    pwd_input = st.text_input("輸入密碼後按 Enter", type="password")
    if pwd_input == TEAM_PASSWORD:
        st.session_state.authenticated = True
        st.rerun()
    elif pwd_input != "":
        st.error("❌ 密碼錯誤，請重新輸入！")
    st.stop()

# ==================== 3. 字典定義區 ====================
base_quality = "masterpiece, best quality, highres, ultra-detailed, 8k resolution"
base_negative = "ugly, deformed, blurry, poor details, bad anatomy, worst quality, low quality, jpeg artifacts, overexposed, underexposed"

dict_style = {
    "寫實商業攝影": "realistic, photorealistic, RAW photo, commercial photography, sharp focus", 
    "高級精品感": "high-end luxury, editorial fashion photography, sleek, sophisticated", 
    "科技未來感": "cyberpunk, sci-fi, futuristic, glowing neon lights, intricate mechanical details", 
    "溫暖生活感": "warm lifestyle, slice of life, cozy atmosphere, candid photography", 
    "年輕潮流感": "trendy streetwear, youth culture, dynamic, vibrant colors", 
    "日系清透": "Japanese aesthetic, clear and airy, muted pastel colors, soft focus, film photography", 
    "歐美廣告劇照": "cinematic still, Hollywood movie aesthetic, dramatic lighting, 35mm photograph", 
    "插畫風": "digital illustration, vibrant colors, flat design, vector art, 2D", 
    "3D 視覺風": "3D render, octane render, unreal engine 5, path tracing, volumetric lighting"
}

dict_shot = {"極特寫": "extreme close-up", "特寫": "close-up", "半身": "medium shot, waist up", "膝上景": "cowboy shot", "全身景": "full body", "遠景": "wide shot, wide angle"}
dict_angle = {
    "平視 (Eye Level)": "eye-level shot, straight-on", 
    "仰視 (Low Angle - 攝影機在下)": "low angle shot, shot from below", 
    "俯視 (High Angle - 攝影機在上)": "high angle shot, shot from above", 
    "傾斜荷蘭角 (Dutch Angle)": "dutch angle, tilted frame"
}
dict_relation = {"直視鏡頭 (Looking at Camera)": "looking at viewer", "過肩鏡頭": "over the shoulder", "第一人稱視角": "first-person view, POV", "旁觀者/側面視角": "profile, side view", "背後跟隨視角": "from behind, back view"}

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

st.title("🚀 AI 圖片提示詞生成器")
st.write("精準控制畫面分鏡，專為 Nano Banana 2 (Stable Diffusion) 引擎打造。")

# --- 【畫面重構模式開關】 ---
st.markdown("---")
col_mode1, col_mode2 = st.columns([1, 3])
with col_mode1:
    is_remake_mode = st.toggle("🔮 開啟「畫面重構」模式", value=False)
with col_mode2:
    if is_remake_mode:
        st.info("🔄 **目前為畫面重構模式**：繼承參考圖 [Image 1] 的外貌、風格與光影。您可以選擇性修改「動作、場景」，並強制應用新的「鏡頭設定」。")
    else:
        st.caption("💡 若需基於一張現有參考圖來改變動作與鏡頭，請開啟此模式。")
st.markdown("---")

# --- 【第一區：核心內容】 ---
st.subheader("1. 畫面核心內容 (Who, Doing What, Where)")
col_text1, col_text2, col_text3 = st.columns(3)
with col_text1:
    user_keyword = st.text_input(
        "📦 畫面主角 (Who) *必填", 
        value="同參考圖主角" if is_remake_mode else "一位穿白襯衫的年輕女性",
        disabled=is_remake_mode,
        help="重構模式下，將強制繼承參考圖主角。" if is_remake_mode else ""
    )
with col_text2:
    user_action = st.text_input(
        "🏃‍♂️ 主角動作 (Doing What)", 
        value="" if is_remake_mode else "手裡拿著咖啡，燦爛微笑", 
        placeholder="例如：手裡拿著咖啡", 
        help="非必填。留白代表不更改動作。" if is_remake_mode else "非必填。"
    )
with col_text3:
    # ⭐ 根據模式動態切換背景是否必填與提示文字
    bg_label = "🖼️ 背景場景 (Where)" if is_remake_mode else "🖼️ 背景場景 (Where) *必填"
    bg_help = "非必填。留白代表不更改背景場景。" if is_remake_mode else ""
    bg_value = "" if is_remake_mode else "陽光明媚的現代咖啡廳"
    
    user_background = st.text_input(bg_label, value=bg_value, help=bg_help)

st.divider()

# --- 【第二區：參考圖數量對應與連動】 ---
img_counter = 1 
ref_prompts = [] 
custom_light_prompt = ""
use_light_ref = False

if not is_remake_mode:
    st.subheader("2. 參考圖片參數設定 (自動計算 Image 編號)")
    st.warning("⚠️ **重要提醒：** 請依照下方 **「人物 ➔ 物件 ➔ 光線」的順序上傳**，否則 [Image X] 的編號會對不起來！")

    col_ref1, col_ref2, col_ref3 = st.columns(3)

    with col_ref1:
        use_char_ref = st.checkbox("👤 啟用人物參考圖")
        if use_char_ref:
            char_count = st.number_input("輸入人物參考圖數量", min_value=1, max_value=10, value=1, step=1)
            char_parts = st.multiselect("請選擇要參考的部位 (可複選)", ["臉部特徵 (Face)", "服裝穿搭 (Clothing)"])
            char_labels = [f"[Image {i}]" for i in range(img_counter, img_counter + char_count)]
            img_counter += char_count 
            parts_map = {"臉部特徵 (Face)": "face", "服裝穿搭 (Clothing)": "clothing"}
            selected_parts = [parts_map[p] for p in char_parts]
            parts_str = f" for {' and '.join(selected_parts)}" if selected_parts else ""
            ref_prompts.append(f"referencing character details from {', '.join(char_labels)}{parts_str}")

    with col_ref2:
        use_obj_ref = st.checkbox("📦 啟用物件參考圖")
        if use_obj_ref:
            obj_count = st.number_input("輸入物件參考圖數量", min_value=1, max_value=10, value=1, step=1)
            obj_attr = st.text_input("請描述物件屬性 (填空)", placeholder="例如：紅色的皮革包包")
            obj_labels = [f"[Image {i}]" for i in range(img_counter, img_counter + obj_count)]
            img_counter += obj_count 
            attr_str = f" as {obj_attr}" if obj_attr else ""
            ref_prompts.append(f"referencing object {', '.join(obj_labels)}{attr_str}")

    with col_ref3:
        use_light_ref = st.checkbox("💡 啟用光線與色調參考圖")
        if use_light_ref:
            light_count = st.number_input("輸入光線參考圖數量", min_value=1, max_value=10, value=1, step=1)
            st.info(f"鎖定下方選單，並佔用 {light_count} 個 Image 編號")
            light_labels = [f"[Image {i}]" for i in range(img_counter, img_counter + light_count)]
            img_counter += light_count 
            custom_light_prompt = f"matching the exact lighting, color grading, and texture of {', '.join(light_labels)}"

    st.divider()

# --- 【第三區：攝影與風格控制】 ---
st.subheader("3. 攝影與風格控制")
col1, col2, col3 = st.columns(3)

with col1:
    style_choice = st.selectbox(
        "✨ 視覺風格", 
        list(dict_style.keys()), 
        disabled=is_remake_mode,
        help="重構模式下由參考圖決定" if is_remake_mode else ""
    )
    light_choice = st.selectbox(
        "💡 光線與色調", 
        list(dict_light.keys()), 
        disabled=use_light_ref or is_remake_mode, 
        help="重構模式下由參考圖決定" if is_remake_mode else ("若啟用光線參考圖，此選項將失效。" if use_light_ref else "")
    )

with col2:
    shot_choice = st.selectbox("🔲 鏡頭大小", list(dict_shot.keys()))
    angle_choice = st.selectbox("📐 鏡頭角度", list(dict_angle.keys()))

with col3:
    relation_choice = st.selectbox("👁️ 鏡頭互動關係", list(dict_relation.keys()))
    ratio_choice = st.selectbox("📏 畫面比例", list(dict_ratio.keys()))
    append_ratio = st.checkbox("☑️ 將比例標籤加入提示詞結尾 (例如: 16:9 aspect ratio)", value=False)

st.divider()

# --- 【第四區：負面提示詞】 ---
st.subheader("4. 負面提示詞 (Negative Prompt) - 選填")
user_negative = st.text_input(
    "🚫 想要排除的額外元素 (請用「空白鍵」隔開不同的詞)", 
    placeholder="例如: text logo watermark ugly trees", 
    help="只要打完單字按空白鍵，系統就會自動幫您轉換成 AI 懂的格式！"
)

st.divider()

# ==================== 5. 產圖邏輯區 ====================

if st.button("🪄 組合咒語 (Generate Prompt)", type="primary", use_container_width=True):
    
    # ⭐ 針對不同模式的必填檢查
    if not is_remake_mode and (user_keyword.strip() == "" or user_background.strip() == ""):
        st.error("⚠️ 一般模式下，請確實填寫「畫面主角」與「背景場景」！")
    else:
        # [處理負面提示詞]
        custom_neg_tags = ""
        if user_negative.strip() != "":
            word_list = [word.strip() for word in user_negative.replace(',', ' ').split() if word.strip()]
            custom_neg_tags = ", ".join(word_list)
        final_negative_prompt = f"{custom_neg_tags}, {base_negative}" if custom_neg_tags else base_negative

        # [處理正向提示詞 - 依照模式分流]
        if is_remake_mode:
            # === 畫面重構模式 ===
            base_prompt = "maintaining the exact subject, visual style, color grading and lighting of [Image 1]"
            
            # 判斷是否有填寫動作與場景，並加入改變的指令
            if user_action.strip():
                base_prompt += f", changing action to: {user_action.strip()}"
            if user_background.strip():
                base_prompt += f", changing background to: {user_background.strip()}"
                
            # ⭐ 明確加上修改鏡頭視角的提示詞
            base_prompt += f", changing camera view to: {dict_shot[shot_choice]}, {dict_angle[angle_choice]}, {dict_relation[relation_choice]}"
            
            final_prompt = base_prompt
            
        else:
            # === 一般生成模式 ===
            subject_and_action = f"{user_keyword}, {user_action}" if user_action.strip() else f"{user_keyword}"
            final_light = custom_light_prompt if use_light_ref else dict_light[light_choice]

            base_prompt = (
                f"{subject_and_action}, "
                f"in {user_background}, "
                f"{dict_shot[shot_choice]}, "
                f"{dict_angle[angle_choice]}, "
                f"{dict_relation[relation_choice]}, "
                f"{dict_style[style_choice]}, "
                f"{final_light}"
            )
            
            final_prompt = base_prompt + ", " + ", ".join(ref_prompts) if ref_prompts else base_prompt

        # 將 Base Quality (畫質詞) 統一補在最後面
        final_prompt += f", {base_quality}"

        # 如果有比例標籤，接在畫質詞之後
        if append_ratio:
            final_prompt += f", {dict_ratio[ratio_choice]}"

        # ---------------- 顯示結果 ----------------
        st.success("✅ 成功生成提示詞！請點擊右上方按鈕一鍵複製。")
        st.markdown("👇 **請將滑鼠移至下方黑框的右上角，點擊出現的「📋」圖示即可一鍵全選複製**")
        
        combined_output = f"{final_prompt}\n\n[Negative Prompt]\n{final_negative_prompt}"
        st.code(combined_output, language="text")
        
        st.info(f"💡 【尺寸參數建議】： 寬度 {1920 if '16:9' in ratio_choice else (1080 if '9:16' in ratio_choice else (1024 if '1:1' in ratio_choice else (1440 if '4:3' in ratio_choice else (1080 if '3:4' in ratio_choice else 2560))))}px, 高度 {1080 if '16:9' in ratio_choice else (1920 if '9:16' in ratio_choice else (1024 if '1:1' in ratio_choice else (1080 if '4:3' in ratio_choice else (1440 if '3:4' in ratio_choice else 1080))))}px")