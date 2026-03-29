# 개요

사내 업무 시 자주 활용되는 LLM API 요청에 대한 **비동기 처리 다목적 스크립트**입니다.

CSV 파일에 요청 목록을 작성해두면, OpenAI / Anthropic(Claude) / Google(Gemini) API에 **동시에 대량 요청**을 보내고 결과를 JSON 파일로 저장합니다.

> **비동기(Async)란?**
> 일반적으로 API 요청은 하나씩 순서대로 처리됩니다. 요청 1개당 수 초가 걸리므로, 100개를 처리하면 수백 초가 걸릴 수 있습니다.
> 비동기 처리는 요청을 동시에 여러 개 보내어 대기 시간을 줄이는 방식입니다. 100개를 보내도 가장 느린 1개의 시간 정도만 기다리면 됩니다.



---



# 사전 준비

## 1. Python 설치 확인

터미널(명령 프롬프트)에서 아래 명령어를 입력하여 Python이 설치되어 있는지 확인합니다.

```
python --version
```

Python 3.10 이상이 필요합니다. 설치가 안 되어 있다면 [python.org](https://www.python.org/downloads/)에서 다운로드하세요.

## 2. 필요 패키지 설치

프로젝트 폴더에서 터미널을 열고 아래 명령어를 실행합니다. (최초 1회만 필요)

```
pip install -r requirements.txt
```

## 3. API 키 설정

프로젝트 폴더의 `.env` 파일을 열고, 사용할 서비스의 API 키를 입력합니다.

```
OPENAI_API_KEY=여기에_OpenAI_키_입력
ANTHROPIC_API_KEY=여기에_Anthropic_키_입력
GOOGLE_API_KEY=여기에_Google_키_입력
```

- 사용하지 않는 서비스의 키는 비워두어도 됩니다.
- API 키는 외부에 절대 공유하지 마세요.



---



# 사용법

## 폴더 구조

```
async_api_call/
│
├── .env                        ← API 키 설정 파일
├── run.bat                     ← 실행 파일 (더블클릭으로 실행 가능)
├── main.py                     ← 메인 스크립트
│
├── settings/
│   └── config.yaml             ← 경로 및 실행 설정
│
├── sample/
│   ├── sample.csv              ← 요청 목록 예시 파일
│   ├── sample_system_prompt.txt← 시스템 프롬프트 예시
│   └── sample_image/           ← 이미지 파일 보관 폴더
│
└── output/                     ← 결과 JSON 파일이 저장되는 폴더
```

---

## Step 1 — 요청 목록 CSV 작성

`sample/sample.csv` 파일을 참고하여 요청 목록을 작성합니다.

| 컬럼 | 필수 여부 | 설명 |
|------|-----------|------|
| `model` | **필수** | 사용할 모델명 (아래 지원 모델 참고) |
| `save_path` | **필수** | 결과를 저장할 파일명 (예: `001.json`) |
| `user_prompt` | 선택 | AI에게 보낼 질문 또는 요청 내용 (시스템 프롬프트만으로 충분할 경우 빈칸 가능) |
| `image_path` | 선택 | 이미지 파일명 (이미지 없으면 빈칸) |

**CSV 예시:**

```csv
model,save_path,image_path,user_prompt
gpt-4o,001.json,,오늘 날씨 어때?
claude-sonnet-4-5,002.json,,Python으로 피보나치 수열 짜줘
gemini-2.5-flash,003.json,photo.jpg,이 이미지를 설명해줘
gpt-4o,004.json,,
```

> - `user_prompt`는 선택 항목입니다. 시스템 프롬프트에 지시사항을 이미 작성한 경우 빈칸으로 두어도 됩니다.
> - 이미지를 사용하려면 `settings/config.yaml`의 `image_file.base_root`에 지정된 폴더에 이미지 파일을 넣고, `image_path`에 파일명만 작성합니다.
> - 이미 결과 파일이 존재하는 행은 자동으로 건너뜁니다. (중복 실행 안전)

---

## Step 2 — 시스템 프롬프트 작성 (선택)

`sample/sample_system_prompt.txt` 파일을 열고, AI에게 공통으로 적용할 역할/지침을 작성합니다.

```
당신은 친절한 업무 보조 AI입니다. 항상 한국어로 답변해주세요.
```

---

## Step 3 — 설정 파일 확인

`settings/config.yaml` 파일에서 경로와 실행 옵션을 설정합니다.

```yaml
path:
  input: ./sample/sample.csv          # 요청 목록 CSV 파일 경로
  system_prompt: ./sample/sample_system_prompt.txt  # 시스템 프롬프트 파일 경로
  output: ./output                    # 결과 저장 폴더 경로

settings:
  request:
    batch_size: 100   # 한 번에 동시 요청할 최대 개수
    retries: 3        # 실패 시 재시도 횟수
    delay: 60         # 재시도 전 대기 시간 (초)

  image_file:
    base_root: ./sample/sample_image  # 이미지 파일 폴더 경로
    suffix: [".png", ".jpg", ".jpeg", ".webp"]  # 허용 이미지 확장자
```

---

## Step 4 — 실행

### 방법 A: 더블클릭으로 실행 (간편)

`run.bat` 파일을 더블클릭합니다.

### 방법 B: 터미널에서 실행

```
python main.py
```

다른 설정 파일을 사용하려면:

```
python main.py --config 설정파일경로/config.yaml
```

---

## Step 5 — 결과 확인

실행이 완료되면 `output/` 폴더 안에 CSV에 지정한 경로로 JSON 파일이 생성됩니다.

각 JSON 파일에는 해당 요청에 대한 AI 응답 결과가 저장됩니다.

---

## 로그 확인

실행 중 발생한 로그는 `logs/` 폴더에 날짜별로 저장됩니다. (예: `logs/2026-03-29.log`)

오류가 발생하면 이 파일을 확인하세요.



---



# 지원 모델

## OpenAI

| 모델명 (CSV에 입력할 값) |
|--------------------------|
| `gpt-5.2` |
| `gpt-5.1` |
| `gpt-5` |
| `gpt-5-mini` |
| `gpt-5-nano` |
| `gpt-5.2-pro` |
| `gpt-5-pro` |
| `gpt-4.1` |
| `gpt-4.1-mini` |
| `gpt-4.1-nano` |
| `gpt-4o` |
| `gpt-4o-mini` |

## Anthropic (Claude)

| 모델명 (CSV에 입력할 값) |
|--------------------------|
| `claude-opus-4-5` |
| `claude-opus-4-1` |
| `claude-opus-4` |
| `claude-sonnet-4-5` |
| `claude-sonnet-4` |
| `claude-haiku-4-5` |
| `claude-haiku-3-5` |
| `claude-haiku-3` |

## Google (Gemini)

| 모델명 (CSV에 입력할 값) |
|--------------------------|
| `gemini-3-flash-preview` |
| `gemini-2.5-pro` |
| `gemini-2.5-flash` |
| `gemini-2.0-flash` |
| `gemini-2.0-flash-lite` |



---



# 자주 묻는 오류

| 오류 메시지 | 원인 및 해결 방법 |
|-------------|-------------------|
| `CSV에 필수 컬럼이 없습니다` | CSV 파일에 `model`, `save_path` 컬럼이 있는지 확인하세요. |
| `이미지 파일을 이미지 폴더에서 찾을 수 없습니다` | `image_path`에 입력한 파일명과 `config.yaml`의 `image_file.base_root` 폴더 안의 파일명이 일치하는지 확인하세요. |
| `API key` 관련 오류 | `.env` 파일에 올바른 API 키가 입력되어 있는지 확인하세요. |
| `ModuleNotFoundError` | `pip install -r requirements.txt`를 실행하지 않은 경우입니다. 다시 실행하세요. |
