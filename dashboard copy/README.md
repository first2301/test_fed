# 연합학습 컨테이너 모니터링 대시보드

FastAPI 기반의 Docker 컨테이너 모니터링 대시보드입니다. 여러 노드의 컨테이너를 관리하고 시각화할 수 있습니다.

## 주요 기능

- 🐳 **컨테이너 모니터링**: 여러 Docker 노드의 컨테이너 상태 실시간 조회
- 📊 **통계 대시보드**: 전체/실행 중/중지된 컨테이너 수 표시
- 🎨 **모던 UI**: 카드 기반 레이아웃과 그라데이션 디자인
- 📈 **그래프 시각화**: Cytoscape.js를 활용한 노드-엣지 그래프
- 🎯 **컨테이너 제어**: 시작/중지/재시작 기능
- 📱 **반응형 디자인**: 모바일 및 데스크톱 지원

## 기술 스택

### Backend
- **FastAPI**: Python 웹 프레임워크
- **Docker SDK**: Docker 컨테이너 관리
- **Jinja2**: 템플릿 엔진

### Frontend
- **Vanilla JavaScript**: 순수 JavaScript
- **Cytoscape.js**: 그래프 시각화 라이브러리
- **Font Awesome**: 아이콘 라이브러리
- **CSS3**: 모던 스타일링 (Glassmorphism, 그라데이션)

## 설치 방법

### 1. Python 의존성 설치

```bash
pip install -r requirements.dash.txt
```

### 2. JavaScript 라이브러리 설치 (npm 사용)

#### 2-1. package.json 생성

프로젝트 루트에 `package.json` 파일이 없으면 생성:

```json
{
  "name": "fl-dashboard",
  "version": "1.0.0",
  "description": "Federated Learning Container Monitoring Dashboard",
  "private": true,
  "scripts": {
    "copy-vendor": "mkdir -p static/js/vendor && cp node_modules/cytoscape/dist/cytoscape.min.js static/js/vendor/ && cp node_modules/dagre/dist/dagre.min.js static/js/vendor/ && cp node_modules/cytoscape-dagre/cytoscape-dagre.js static/js/vendor/"
  },
  "dependencies": {
    "cytoscape": "^3.27.0",
    "dagre": "^0.8.5",
    "cytoscape-dagre": "^2.5.0"
  }
}
```

#### 2-2. npm 패키지 설치

```bash
npm install
```

#### 2-3. vendor 파일 복사

**Windows:**
```bash
mkdir static\js\vendor
copy node_modules\cytoscape\dist\cytoscape.min.js static\js\vendor\
copy node_modules\dagre\dist\dagre.min.js static\js\vendor\
copy node_modules\cytoscape-dagre\cytoscape-dagre.js static\js\vendor\
```

**Linux/Mac:**
```bash
npm run copy-vendor
# 또는 수동으로:
mkdir -p static/js/vendor
cp node_modules/cytoscape/dist/cytoscape.min.js static/js/vendor/
cp node_modules/dagre/dist/dagre.min.js static/js/vendor/
cp node_modules/cytoscape-dagre/cytoscape-dagre.js static/js/vendor/
```

### 3. HTML 파일 수정

`templates/index.html`에서 CDN 링크를 로컬 파일로 변경:

```html
<!-- CDN (제거) -->
<!-- <script src="https://unpkg.com/cytoscape@3.27.0/dist/cytoscape.min.js"></script> -->
<!-- <script src="https://unpkg.com/dagre@0.8.5/dist/dagre.min.js"></script> -->
<!-- <script src="https://unpkg.com/cytoscape-dagre@2.5.0/cytoscape-dagre.js"></script> -->

<!-- 로컬 파일 (사용) -->
<script src="/static/js/vendor/cytoscape.min.js"></script>
<script src="/static/js/vendor/dagre.min.js"></script>
<script src="/static/js/vendor/cytoscape-dagre.js"></script>
```

## 실행 방법

### 개발 모드

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker 사용

```bash
docker build -f Dockerfile.dash -t fl-dashboard .
docker run -p 8000:8000 -v /var/run/docker.sock:/var/run/docker.sock fl-dashboard
```

## 프로젝트 구조

```
dashboard/
├── app/
│   ├── __init__.py
│   └── main.py              # FastAPI 애플리케이션
├── static/
│   ├── css/
│   │   └── style.css        # 스타일시트
│   └── js/
│       ├── main.js          # 메인 JavaScript
│       └── vendor/           # 외부 라이브러리 (npm 설치 후)
│           ├── cytoscape.min.js
│           ├── dagre.min.js
│           └── cytoscape-dagre.js
├── templates/
│   └── index.html           # 메인 템플릿
├── node_modules/            # npm 패키지 (gitignore)
├── package.json             # npm 의존성
├── package-lock.json        # npm 잠금 파일 (gitignore)
├── requirements.dash.txt    # Python 의존성
├── Dockerfile.dash          # Docker 이미지 빌드
└── README.md                # 이 파일
```

## 설정

### Docker 노드 추가

`app/main.py`의 `DOCKER_HOSTS` 딕셔너리에 노드 추가:

```python
DOCKER_HOSTS = {
    "local": {"base_url": "unix://var/run/docker.sock", "label": "로컬 서버"},
    "node1": {"base_url": "tcp://10.0.0.5:2376", "label": "병원 A 서버"},
    "node2": {"base_url": "tcp://10.0.0.6:2376", "label": "병원 B 서버"},
}
```

## API 엔드포인트

- `GET /`: 메인 대시보드 페이지
- `GET /api/nodes`: 노드 목록 조회
- `GET /api/containers?node_id={node_id}`: 컨테이너 목록 조회
- `POST /api/containers/start`: 컨테이너 시작
- `POST /api/containers/stop`: 컨테이너 중지
- `POST /api/containers/restart`: 컨테이너 재시작

## 주요 기능 설명

### 통계 대시보드
- 전체 컨테이너 수
- 실행 중인 컨테이너 수
- 중지된 컨테이너 수

### 테이블/그래프 뷰
- **테이블 보기**: 카드 그리드 레이아웃으로 컨테이너 정보 표시
- **그래프 보기**: 노드-엣지 그래프로 컨테이너 관계 시각화

### 컨테이너 제어
- 각 컨테이너 카드에서 시작/중지/재시작 버튼 제공
- 상태에 따라 버튼 활성화/비활성화

## 개발 환경

- Python 3.10+
- Node.js 16+ (npm 설치 시)
- Docker (컨테이너 관리)

## 라이선스

내부 사용 프로젝트

## 참고사항

- Docker 소켓 접근 권한이 필요합니다 (`/var/run/docker.sock`)
- 원격 Docker 노드 접근 시 TLS 설정이 필요할 수 있습니다
- 프로덕션 환경에서는 CDN 대신 로컬 파일 사용을 권장합니다

