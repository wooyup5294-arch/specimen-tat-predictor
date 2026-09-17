import streamlit as st
import pandas as pd
from datetime import datetime, timedelta


# ============================================================
# 1. 페이지 설정
# ============================================================

st.set_page_config(
    page_title="Specimen TAT System",
    page_icon="🧪",
    layout="wide"
)


# ============================================================
# 2. 사용자
# ============================================================

USERS = {
    "L1001": {
        "password": "1111",
        "name": "이OO",
        "role": "임상병리사"
    },
    "L1002": {
        "password": "2222",
        "name": "김OO",
        "role": "임상병리사"
    },
    "N2001": {
        "password": "3333",
        "name": "박OO",
        "role": "간호사"
    },
    "N2002": {
        "password": "4444",
        "name": "최OO",
        "role": "간호사"
    }
}


# ============================================================
# 3. 부서 / 장비
# ============================================================

DEPARTMENT_DEVICES = {
    "진단혈액": ["XN-20", "STAGO"],
    "임상화학": ["cobas"],
    "진단면역": ["ANILITY"]
}

ALL_DEVICES = [
    "XN-20",
    "STAGO",
    "cobas",
    "ANILITY"
]


# ============================================================
# 4. 장비 상태
# ============================================================

DEVICE_STATUS_OPTIONS = [
    "정상",
    "QC",
    "보정",
    "점검",
    "시약 교체",
    "ERROR"
]


# ============================================================
# 5. 검사별 기본 TAT
# ============================================================

TEST_BASE_TAT = {
    "CBC": 34,
    "CBC+ESR": 49,
    "COAGULATION": 46,
    "ADMISSION BATTERY": 60,
    "CARDIAC MARKER": 60
}


# ============================================================
# 6. 추가 지연시간
# ============================================================

SLIDE_DELAY = 50
RERUN_DELAY = 20
HEMATOLOGY_QC_DELAY = 15


GENERAL_STATUS_DELAY = {
    "정상": 0,
    "QC": 20,
    "보정": 30,
    "점검": 40,
    "시약 교체": 15,
    "ERROR": 0
}


# ============================================================
# 7. 검사 → 장비
# ============================================================

TEST_DEVICE = {
    "CBC": "XN-20",
    "CBC+ESR": "XN-20",
    "COAGULATION": "STAGO",
    "ADMISSION BATTERY": "cobas",
    "CARDIAC MARKER": "ANILITY"
}


# ============================================================
# 8. 검사 → 담당 부서
# ============================================================

TEST_DEPARTMENT = {
    "CBC": "진단혈액",
    "CBC+ESR": "진단혈액",
    "COAGULATION": "진단혈액",
    "ADMISSION BATTERY": "임상화학",
    "CARDIAC MARKER": "진단면역"
}


# ============================================================
# 9. 전화번호 - 테스트용
# ============================================================

DEPARTMENT_PHONE = {
    "진단혈액": "1234",
    "임상화학": "1236",
    "진단면역": "1237"
}


# ============================================================
# 10. 로그인 상태
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None


# ============================================================
# 11. 장비 상태 초기화
# ============================================================

for device in ALL_DEVICES:

    if f"power_{device}" not in st.session_state:
        st.session_state[f"power_{device}"] = True

    if f"status_{device}" not in st.session_state:
        st.session_state[f"status_{device}"] = "정상"

    if f"previous_status_{device}" not in st.session_state:
        st.session_state[f"previous_status_{device}"] = "정상"

    if f"qc_start_{device}" not in st.session_state:
        st.session_state[f"qc_start_{device}"] = None

    if f"error_start_{device}" not in st.session_state:
        st.session_state[f"error_start_{device}"] = None

    if f"recovery_time_{device}" not in st.session_state:
        st.session_state[f"recovery_time_{device}"] = None


# ============================================================
# 12. 로그인 화면
# ============================================================

if not st.session_state.logged_in:

    st.title("🧪 Specimen TAT System")
    st.subheader("🔐 로그인")

    col1, col2 = st.columns(2)

    with col1:
        employee_id = st.text_input(
            "사번",
            placeholder="예: L1001"
        )

    with col2:
        password = st.text_input(
            "비밀번호",
            type="password"
        )

    if st.button(
        "로그인",
        type="primary",
        use_container_width=True
    ):

        employee_id = employee_id.strip().upper()

        if employee_id not in USERS:

            st.error(
                "등록되지 않은 사번입니다."
            )

        elif USERS[employee_id]["password"] != password:

            st.error(
                "비밀번호가 올바르지 않습니다."
            )

        else:

            st.session_state.logged_in = True

            st.session_state.user = {
                "employee_id": employee_id,
                "name": USERS[employee_id]["name"],
                "role": USERS[employee_id]["role"]
            }

            st.rerun()

    st.info(
        "테스트 계정 | "
        "임상병리사 L1001 / 1111 | "
        "간호사 N2001 / 3333"
    )

    st.stop()


# ============================================================
# 13. 로그인 사용자
# ============================================================

user = st.session_state.user

user_name = user["name"]
user_role = user["role"]
employee_id = user["employee_id"]


# ============================================================
# 14. 상단 화면
# ============================================================

col1, col2 = st.columns([8, 2])

with col1:

    st.title(
        "🧪 Specimen TAT System"
    )

    st.caption(
        "가접수시간과 검사실 상황을 반영하여 "
        "검체 결과시간을 제공합니다."
    )

with col2:

    st.write(
        f"👤 **{user_name}**"
    )

    st.caption(
        f"{user_role} · {employee_id}"
    )

    if st.button(
        "로그아웃",
        use_container_width=True
    ):

        st.session_state.logged_in = False
        st.session_state.user = None

        st.rerun()


st.divider()


# ============================================================
# 15. 현재 시간
# ============================================================

col1, col2 = st.columns([9, 1])

with col1:

    st.caption(
        "🕐 현재 기준시각 : "
        + datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

with col2:

    if st.button(
        "🔄 새로고침",
        use_container_width=True
    ):
        st.rerun()


# ============================================================
# 16. 검체 생성 함수
# ============================================================

def make_specimen(
    barcode,
    name,
    patient_id,
    specimen_name,
    source_type,
    source,
    minutes_ago,
    test,
    slide_required=False,
    rerun=False
):

    receipt_time = (
        datetime.now()
        - timedelta(minutes=minutes_ago)
    )

    # 장비 검사 완료 시각
    analyzer_finish_time = (
        receipt_time
        + timedelta(
            minutes=TEST_BASE_TAT[test]
        )
    )

    return {
        "barcode": barcode,
        "name": name,
        "patient_id": patient_id,
        "specimen_name": specimen_name,
        "source_type": source_type,
        "source": source,
        "pre_receipt_time": receipt_time,
        "test": test,
        "slide_required": slide_required,
        "rerun": rerun,
        "analyzer_finish_time": analyzer_finish_time
    }


# ============================================================
# 17. 가상 검체
# ============================================================

if "specimens_v12" not in st.session_state:

    st.session_state.specimens_v12 = [

        # 81병동

        make_specimen(
            "260917001",
            "김OO",
            "10000101",
            "EDTA Whole Blood",
            "병동",
            "81병동",
            10,
            "CBC"
        ),

        # 이미 장비 검사가 끝나서
        # 슬라이드 확인 단계에 있는 예시
        make_specimen(
            "260917002",
            "이OO",
            "10000102",
            "EDTA Whole Blood",
            "병동",
            "81병동",
            45,
            "CBC",
            slide_required=True
        ),

        make_specimen(
            "260917003",
            "박OO",
            "10000103",
            "EDTA Whole Blood",
            "병동",
            "81병동",
            20,
            "CBC+ESR"
        ),

        make_specimen(
            "260917004",
            "최OO",
            "10000104",
            "Citrate Plasma",
            "병동",
            "81병동",
            15,
            "COAGULATION"
        ),

        make_specimen(
            "260917005",
            "정OO",
            "10000105",
            "Serum",
            "병동",
            "81병동",
            12,
            "ADMISSION BATTERY"
        ),

        make_specimen(
            "260917006",
            "한OO",
            "10000106",
            "Serum",
            "병동",
            "81병동",
            8,
            "CARDIAC MARKER"
        ),


        # 72병동

        make_specimen(
            "260917007",
            "윤OO",
            "10000107",
            "EDTA Whole Blood",
            "병동",
            "72병동",
            7,
            "CBC"
        ),

        make_specimen(
            "260917008",
            "강OO",
            "10000108",
            "EDTA Whole Blood",
            "병동",
            "72병동",
            25,
            "CBC+ESR"
        ),

        make_specimen(
            "260917009",
            "조OO",
            "10000109",
            "EDTA Whole Blood",
            "병동",
            "72병동",
            50,
            "CBC",
            slide_required=True
        ),

        make_specimen(
            "260917010",
            "임OO",
            "10000110",
            "Citrate Plasma",
            "병동",
            "72병동",
            19,
            "COAGULATION"
        ),

        make_specimen(
            "260917011",
            "신OO",
            "10000111",
            "Serum",
            "병동",
            "72병동",
            17,
            "ADMISSION BATTERY",
            rerun=True
        ),

        make_specimen(
            "260917012",
            "장OO",
            "10000112",
            "Serum",
            "병동",
            "72병동",
            9,
            "CARDIAC MARKER"
        ),


        # 91병동

        make_specimen(
            "260917013",
            "오OO",
            "10000113",
            "EDTA Whole Blood",
            "병동",
            "91병동",
            11,
            "CBC"
        ),

        make_specimen(
            "260917014",
            "문OO",
            "10000114",
            "EDTA Whole Blood",
            "병동",
            "91병동",
            60,
            "CBC+ESR",
            slide_required=True
        ),

        make_specimen(
            "260917015",
            "노OO",
            "10000115",
            "Citrate Plasma",
            "병동",
            "91병동",
            22,
            "COAGULATION"
        ),

        make_specimen(
            "260917016",
            "권OO",
            "10000116",
            "Serum",
            "병동",
            "91병동",
            12,
            "ADMISSION BATTERY"
        ),

        make_specimen(
            "260917017",
            "백OO",
            "10000117",
            "Serum",
            "병동",
            "91병동",
            14,
            "CARDIAC MARKER",
            rerun=True
        ),


        # 혈액내과

        make_specimen(
            "260917018",
            "남OO",
            "10000118",
            "EDTA Whole Blood",
            "외래",
            "혈액내과",
            8,
            "CBC"
        ),

        make_specimen(
            "260917019",
            "배OO",
            "10000119",
            "EDTA Whole Blood",
            "외래",
            "혈액내과",
            20,
            "CBC+ESR"
        ),

        make_specimen(
            "260917020",
            "류OO",
            "10000120",
            "Citrate Plasma",
            "외래",
            "혈액내과",
            25,
            "COAGULATION"
        ),


        # 순환기내과

        make_specimen(
            "260917021",
            "안OO",
            "10000121",
            "Serum",
            "외래",
            "순환기내과",
            6,
            "CARDIAC MARKER"
        ),

        make_specimen(
            "260917022",
            "전OO",
            "10000122",
            "Serum",
            "외래",
            "순환기내과",
            16,
            "CARDIAC MARKER",
            rerun=True
        ),

        make_specimen(
            "260917023",
            "홍OO",
            "10000123",
            "Serum",
            "외래",
            "순환기내과",
            13,
            "ADMISSION BATTERY"
        ),


        # 응급의학과

        make_specimen(
            "260917024",
            "유OO",
            "10000124",
            "EDTA Whole Blood",
            "외래",
            "응급의학과",
            5,
            "CBC"
        ),

        make_specimen(
            "260917025",
            "고OO",
            "10000125",
            "EDTA Whole Blood",
            "외래",
            "응급의학과",
            14,
            "CBC+ESR"
        ),

        make_specimen(
            "260917026",
            "차OO",
            "10000126",
            "Citrate Plasma",
            "외래",
            "응급의학과",
            11,
            "COAGULATION"
        ),

        make_specimen(
            "260917027",
            "성OO",
            "10000127",
            "Serum",
            "외래",
            "응급의학과",
            9,
            "CARDIAC MARKER"
        ),

        make_specimen(
            "260917028",
            "하OO",
            "10000128",
            "Serum",
            "외래",
            "응급의학과",
            15,
            "ADMISSION BATTERY"
        ),

        make_specimen(
            "260917029",
            "김OO",
            "10000129",
            "EDTA Whole Blood",
            "외래",
            "응급의학과",
            55,
            "CBC",
            slide_required=True
        )
    ]


# ============================================================
# 18. 장비 상태 변화 기록
# ============================================================

def update_device_state(device):

    current = st.session_state[
        f"status_{device}"
    ]

    previous = st.session_state[
        f"previous_status_{device}"
    ]

    now = datetime.now()


    # --------------------------------------------------------
    # QC 시작
    # --------------------------------------------------------

    if (
        current == "QC"
        and previous != "QC"
    ):

        st.session_state[
            f"qc_start_{device}"
        ] = now


    # --------------------------------------------------------
    # ERROR 시작
    # --------------------------------------------------------

    if (
        current == "ERROR"
        and previous != "ERROR"
    ):

        st.session_state[
            f"error_start_{device}"
        ] = now

        st.session_state[
            f"recovery_time_{device}"
        ] = None


    # --------------------------------------------------------
    # ERROR → 정상
    # --------------------------------------------------------

    if (
        previous == "ERROR"
        and current == "정상"
    ):

        st.session_state[
            f"recovery_time_{device}"
        ] = now


    st.session_state[
        f"previous_status_{device}"
    ] = current


# ============================================================
# 19. 결과시간 계산
# ============================================================

def calculate_result(specimen):

    now = datetime.now()

    test = specimen["test"]

    device = TEST_DEVICE[test]

    department = TEST_DEPARTMENT[test]

    base_tat = TEST_BASE_TAT[test]

    receipt_time = specimen[
        "pre_receipt_time"
    ]

    original_analyzer_finish = specimen[
        "analyzer_finish_time"
    ]


    power = st.session_state[
        f"power_{device}"
    ]

    device_status = st.session_state[
        f"status_{device}"
    ]

    qc_start = st.session_state[
        f"qc_start_{device}"
    ]

    error_start = st.session_state[
        f"error_start_{device}"
    ]

    recovery_time = st.session_state[
        f"recovery_time_{device}"
    ]


    # ========================================================
    # A. 이미 장비 검사를 완료했는가?
    # ========================================================

    analyzer_already_finished = (
        now >= original_analyzer_finish
    )


    # ========================================================
    # B. Slide 단계에 이미 들어간 CBC
    #
    # 이 검체는 장비를 이미 빠져나왔기 때문에
    # 이후 QC / ERROR 영향 없음
    # ========================================================

    if (
        specimen["slide_required"]
        and test in ["CBC", "CBC+ESR"]
        and analyzer_already_finished
    ):

        result_time = (
            original_analyzer_finish
            + timedelta(
                minutes=SLIDE_DELAY
            )
        )

        return {
            "device": device,
            "result_time":
                result_time.strftime("%H:%M"),
            "reason": "슬라이드 확인"
        }


    # ========================================================
    # C. 장비 검사를 이미 끝낸 일반 검체
    #
    # 이후 장비 상태 변화에 영향 없음
    # ========================================================

    if analyzer_already_finished:

        extra_delay = 0
        reasons = []


        # ADMISSION / CARDIAC 재검
        if (
            specimen["rerun"]
            and test in [
                "ADMISSION BATTERY",
                "CARDIAC MARKER"
            ]
        ):

            extra_delay += RERUN_DELAY
            reasons.append("재검")


        result_time = (
            original_analyzer_finish
            + timedelta(
                minutes=extra_delay
            )
        )


        reason = (
            " + ".join(reasons)
            if reasons
            else "-"
        )


        return {
            "device": device,
            "result_time":
                result_time.strftime("%H:%M"),
            "reason": reason
        }


    # ========================================================
    # 여기부터는 아직 장비검사가 끝나지 않은 검체
    # ========================================================


    # ========================================================
    # D. 장비 전원 OFF
    # ========================================================

    if not power:

        return {
            "device": device,
            "result_time": "-",
            "reason": "장비 전원 OFF"
        }


    # ========================================================
    # E. 진단혈액 ERROR
    #
    # ERROR 발생 전에 장비검사를 끝낸 검체는
    # 위에서 이미 제외됨.
    #
    # 현재 ERROR 상태인 미완료 검체만 영향.
    # ========================================================

    if (
        department == "진단혈액"
        and device_status == "ERROR"
    ):

        return {
            "device": device,
            "result_time": "-",
            "reason": "장비 ERROR"
        }


    # ========================================================
    # F. ERROR → 정상화
    #
    # ERROR가 시작될 당시 아직 검사가 끝나지 않았던
    # 검체만 정상화 시각부터 다시 계산
    # ========================================================

    if (
        department == "진단혈액"
        and device_status == "정상"
        and error_start is not None
        and recovery_time is not None
        and original_analyzer_finish > error_start
        and receipt_time <= recovery_time
    ):

        result_time = (
            recovery_time
            + timedelta(
                minutes=base_tat
            )
        )


        # Slide는 아직 검사 후 단계이므로
        # 여기서는 바로 추가하지 않음.

        return {
            "device": device,
            "result_time":
                result_time.strftime("%H:%M"),
            "reason": "장비 ERROR"
        }


    # ========================================================
    # G. 진단혈액 QC
    #
    # QC 시작 전에 이미 장비검사를 끝낸 검체는
    # 위에서 제외됨.
    #
    # QC 시작 당시 미완료 검체만 +15분
    # ========================================================

    if (
        department == "진단혈액"
        and device_status == "QC"
        and qc_start is not None
        and original_analyzer_finish > qc_start
    ):

        result_time = (
            receipt_time
            + timedelta(
                minutes=
                    base_tat
                    + HEMATOLOGY_QC_DELAY
            )
        )

        return {
            "device": device,
            "result_time":
                result_time.strftime("%H:%M"),
            "reason": "QC"
        }


    # ========================================================
    # H. 기타 장비 상태
    # ========================================================

    extra_delay = 0
    reasons = []


    if device_status != "정상":

        delay = GENERAL_STATUS_DELAY.get(
            device_status,
            0
        )

        extra_delay += delay

        reasons.append(
            device_status
        )


    # ========================================================
    # I. 재검
    # ========================================================

    if (
        specimen["rerun"]
        and test in [
            "ADMISSION BATTERY",
            "CARDIAC MARKER"
        ]
    ):

        extra_delay += RERUN_DELAY

        reasons.append(
            "재검"
        )


    # ========================================================
    # J. 일반 결과시간
    # ========================================================

    result_time = (
        receipt_time
        + timedelta(
            minutes=
                base_tat
                + extra_delay
        )
    )


    reason = (
        " + ".join(reasons)
        if reasons
        else "-"
    )


    return {
        "device": device,
        "result_time":
            result_time.strftime("%H:%M"),
        "reason": reason
    }


# ============================================================
# 20. 표 데이터
# ============================================================

def build_rows():

    rows = []

    for specimen in (
        st.session_state.specimens_v12
    ):

        result = calculate_result(
            specimen
        )

        department = TEST_DEPARTMENT[
            specimen["test"]
        ]

        rows.append({

            "바코드":
                specimen["barcode"],

            "이름":
                specimen["name"],

            "등록번호":
                specimen["patient_id"],

            "검체명":
                specimen["specimen_name"],

            "구분":
                specimen["source_type"],

            "의뢰부서":
                specimen["source"],

            "검사":
                specimen["test"],

            "가접수시간":
                specimen[
                    "pre_receipt_time"
                ].strftime("%H:%M"),

            "결과시간":
                result["result_time"],

            "지연 사유":
                result["reason"],

            "담당 부서":
                department,

            "문의 전화":
                DEPARTMENT_PHONE[
                    department
                ],

            "장비":
                result["device"]
        })

    return rows


# ============================================================
# 21. 임상병리사 화면
# ============================================================

if user_role == "임상병리사":

    st.header(
        "🔬 검사실"
    )


    # ========================================================
    # 담당 부서 선택
    # ========================================================

    selected_department = st.selectbox(
        "담당 부서 선택",
        [
            "진단혈액",
            "임상화학",
            "진단면역"
        ]
    )


    st.divider()


    # ========================================================
    # 장비 상태
    # ========================================================

    st.subheader(
        f"⚙️ {selected_department} 장비 상태"
    )


    selected_devices = (
        DEPARTMENT_DEVICES[
            selected_department
        ]
    )


    h1, h2, h3 = st.columns(
        [2, 1, 2]
    )

    h1.markdown("**장비**")
    h2.markdown("**전원**")
    h3.markdown("**장비 상태**")


    for device in selected_devices:

        c1, c2, c3 = st.columns(
            [2, 1, 2]
        )


        with c1:

            st.markdown(
                f"**{device}**"
            )


        with c2:

            st.toggle(
                "ON",
                key=f"power_{device}",
                label_visibility="collapsed"
            )


        with c3:

            st.selectbox(
                "장비 상태",
                DEVICE_STATUS_OPTIONS,
                key=f"status_{device}",
                label_visibility="collapsed"
            )


        # 장비 상태 변경시각 저장
        update_device_state(
            device
        )


    st.divider()


    # ========================================================
    # 검체 목록
    # ========================================================

    st.subheader(
        f"🧪 {selected_department} 검체"
    )


    barcode_search = st.text_input(
        "📷 환자 바코드 검색",
        placeholder=
            "바코드를 입력하거나 스캔하세요"
    )


    df = pd.DataFrame(
        build_rows()
    )


    department_df = df[
        df["담당 부서"]
        == selected_department
    ]


    if barcode_search.strip():

        department_df = department_df[
            department_df["바코드"]
            == barcode_search.strip()
        ]


    st.caption(
        f"조회 검체 : "
        f"{len(department_df)}건"
    )


    lab_columns = [
        "바코드",
        "이름",
        "등록번호",
        "검체명",
        "검사",
        "가접수시간",
        "결과시간",
        "지연 사유",
        "장비"
    ]


    if len(department_df) > 0:

        st.dataframe(
            department_df[
                lab_columns
            ],
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "해당 부서의 검체가 없습니다."
        )


# ============================================================
# 22. 간호사 화면
# ============================================================

else:

    st.header(
        "🏥 병동 · 외래 검체 조회"
    )


    col1, col2 = st.columns(
        [1, 2]
    )


    with col1:

        source_type = st.radio(
            "구분",
            [
                "병동",
                "외래"
            ],
            horizontal=True
        )


    available_sources = sorted({

        specimen["source"]

        for specimen
        in st.session_state.specimens_v12

        if specimen["source_type"]
        == source_type
    })


    with col2:

        selected_source = st.selectbox(
            "병동 / 진료과",
            available_sources
        )


    # ========================================================
    # 바코드 검색
    # ========================================================

    barcode_search = st.text_input(
        "📷 환자 바코드 검색",
        placeholder=
            "바코드를 입력하거나 스캔하세요"
    )


    # ========================================================
    # 검체 조회
    # ========================================================

    df = pd.DataFrame(
        build_rows()
    )


    nurse_df = df[
        (df["구분"] == source_type)
        &
        (
            df["의뢰부서"]
            == selected_source
        )
    ]


    if barcode_search.strip():

        nurse_df = nurse_df[
            nurse_df["바코드"]
            == barcode_search.strip()
        ]


    st.caption(
        f"조회 검체 : "
        f"{len(nurse_df)}건"
    )


    nurse_columns = [
        "바코드",
        "이름",
        "등록번호",
        "검체명",
        "검사",
        "가접수시간",
        "결과시간",
        "지연 사유",
        "담당 부서",
        "문의 전화"
    ]


    if len(nurse_df) > 0:

        st.dataframe(
            nurse_df[
                nurse_columns
            ],
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "조건에 해당하는 검체가 없습니다."
        )