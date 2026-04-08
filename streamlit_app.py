import streamlit as st

# ==================== 1. 網頁基本設定 ====================
st.set_page_config(layout="wide", page_title="AI 圖片提示詞生成器")

# ==================== 2. 簡易密碼鎖設定 ====================
# ⭐ 更新通關密碼
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
dict_style = {"寫實商業攝影": "realistic commercial photography, highly detailed, photorealistic", "高級精品感": "high-end luxury aesthetic, sleek, editorial fashion photography", "科技未來感": "cyberpunk, sci-fi futuristic, glowing neon aesthetics", "溫暖生活感": "warm lifestyle photography, cozy atmosphere, candid", "年輕潮流感": "youthful trendy vibe, streetwear aesthetics, dynamic", "日系清透": "Japanese clear aesthetic, soft airy vibe, muted pastel colors", "歐美廣告劇照": "cinematic commercial still, dramatic movie aesthetic, 35mm film", "插畫風": "digital illustration, vector art style, flat design", "3D 視覺風": "3D render, Octane render, Unreal Engine 5, Pixar style"}
dict_shot = {"極特寫": "extreme close-up shot, macro photography", "特寫": "close-up shot", "半身": "medium shot, waist up", "膝上景": "cowboy shot, knee up shot", "全身景": "full body shot", "遠景": "wide shot, long shot"}
dict_angle = {"平視": "eye-level shot", "仰視": "low angle shot", "俯視": "high angle shot", "傾斜荷蘭角": "Dutch angle, tilted frame"}
dict_relation = {"直視鏡頭 (Looking at Camera)": "looking directly at viewer", "過肩鏡頭": "over the shoulder shot, OTS", "第一人稱視角": "first-person view, POV", "旁觀者/側面視角": "profile shot, side view", "背後跟隨視角": "shot from behind, back view"}
dict_light = {"白天自然光": "bright natural sunlight", "黃昏日落暖光 (Magic hour)": "golden hour lighting", "夜晚": "night time, ambient night lighting", "棚拍柔光": "soft studio lighting, softbox", "高反差戲劇光": "dramatic high contrast lighting, chiaroscuro", "冷色科技光": "cool color palette, blue and teal lighting"}

# ==================== 4. UI 介面設計 ====================

# ⭐ 更新網頁大標題
st.title("🚀 AI 圖片提示詞生成器")
st.write("精準控制畫面分鏡，自動計算參考圖編號對應 Prompt。")

# --- 【第一區：核心內容】 ---
st.subheader("1. 畫面核心內容 (Who, Doing What, Where)")
col_text1, col_text2, col_text3 = st.columns(3)
with col_text1:
    user_keyword = st.text_input("📦 畫面主角 (Who) *必填", "一位穿白襯衫的年輕女性")
with col_text2:
    user_action = st.text_input("🏃‍♂️ 主角動作 (Doing What)", "手裡拿著咖啡，燦爛微笑", help="非必填。若主角是產品可保持空白。")
with col_text3:
    user_background = st.text_input("🖼️ 背景場景 (Where) *必填", "陽光明媚的現代咖啡廳")

st.divider()

# --- 【第二區：參考圖數量對應與連動】 ---
st.subheader("2. 參考圖片參數設定 (自動計算 Image 編號)")
st.warning("⚠️ **重要提醒：** 請在主介面上傳圖片時，務必依照下方 **「人物 ➔ 物件 ➔ 光線」的先後順序上傳**，否則 [Image X] 的編號會無法正確對應！")

# 設定一個全域計數器，用來動態計算 Image X 的數字
img_counter = 1 
ref_prompts = [] # 用來儲存組合好的參考圖 Prompt

col_ref1, col_ref2, col_ref3 = st.columns(3)

# 2.1 人物參考圖
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

# 2.2 物件參考圖
with col_ref2:
    use_obj_ref = st.checkbox("📦 啟用物件參考圖")
    if use_obj_ref:
        obj_count = st.number_input("輸入物件參考圖數量", min_value=1, max_value=10, value=1, step=1)
        obj_attr = st.text_input("請描述物件屬性 (填空)", placeholder="例如：紅色的皮革包包")
        
        obj_labels = [f"[Image {i}]" for i in range(img_counter, img_counter + obj_count)]
        img_counter += obj_count 
        
        attr_str = f" as {obj_attr}" if obj_attr else ""
        ref_prompts.append(f"referencing object {', '.join(obj_labels)}{attr_str}")

# 2.3 光線與色調參考圖
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
    style_choice = st.selectbox("✨ 視覺風格", list(dict_style.keys()))
    
    light_choice = st.selectbox(
        "💡 光線與色調", 
        list(dict_light.keys()), 
        disabled=use_light_ref, 
        help="若啟用光線參考圖，此選項將自動反灰失效。" if use_light_ref else ""
    )

with col2:
    shot_choice = st.selectbox("🔲 鏡頭大小", list(dict_shot.keys()))
    angle_choice = st.selectbox("📐 鏡頭角度", list(dict_angle.keys()))

with col3:
    relation_choice = st.selectbox("👁️ 鏡頭互動關係", list(dict_relation.keys()))
    ratio_choice = st.selectbox("📏 提案畫面比例", ["橫式簡報滿版 (16:9)", "IG限動 (9:16)", "方形 (1:1)"])

st.divider()

# ==================== 5. 產圖邏輯區 ====================

if st.button("🪄 組合咒語 (Generate Prompt)", type="primary", use_container_width=True):
    
    if user_keyword.strip() == "" or user_background.strip() == "":
        st.error("⚠️ 請至少填寫「畫面主角」與「背景場景」！")
    else:
        # 1. 處理主角與動作
        subject_and_action = f"{user_keyword} {user_action}" if user_action.strip() else f"{user_keyword}"

        # 2. 處理光線邏輯
        final_light = custom_light_prompt if use_light_ref else dict_light[light_choice]

        # 3. 組合主體 Prompt
        base_prompt = (
            f"{dict_style[style_choice]}, "
            f"{dict_shot[shot_choice]}, "
            f"{dict_angle[angle_choice]}, "
            f"{subject_and_action}, "
            f"{dict_relation[relation_choice]}, "
            f"in {user_background}, "
            f"{final_light}"
        )
        
        # 4. 加上參考圖 Prompt
        if ref_prompts:
            final_prompt = base_prompt + ", " + ", ".join(ref_prompts)
        else:
            final_prompt = base_prompt
        
        st.success("✅ 成功生成提示詞 (Prompt)！")
        st.markdown("👇 **請將滑鼠移至下方黑框的右上角，點擊出現的「📋」圖示即可一鍵複製：**")
        st.code(final_prompt, language="text")
        
        # 計算寬高參數顯示
        width, height = 1920, 1080
        if "9:16" in ratio_choice: width, height = 1080, 1920
        elif "1:1" in ratio_choice: width, height = 1024, 1024
            
        st.info(f"⚙️ 建議在主介面設定的尺寸參數：寬度 {width}px, 高度 {height}px")