# 지후니우스 작업 규칙 (AI·사람 공통)

**시작 전에 `docs/HANDOFF.md`(현재 상태·진행 중 작업·디자인 시안)를 먼저 읽는다.**

- `apps/jihunius/app.pyw`, `dist/`, `releases/`는 **빌드 결과물**이다. 직접 고치지 말고 `src/`·`assets/`를 고친 뒤 `python tools/build_app.py`로 만든다. 구조는 README의 "소스 구조와 빌드" 참고.
- 기존 기능은 **온전히** 유지한다. 속도 개선·디자인 변경도 기능 동작을 바꾸면 안 된다.
- 배포 = `main`의 `channels/stable.json` 변경이다. 사용자가 "배포해줘"라고 할 때만 `tools/prepare_release.py`로 새 버전을 만들어 main에 올린다. 그 외 작업은 작업 브랜치에서 한다.
- 이미 올린 `releases/jihunius/<버전>/`은 절대 덮어쓰지 않는다.
- 배포를 마치면 Google Drive `일 → CNC 스크립트` 폴더(ID `1KP9uERp5XFxvIoSTfcSrsOmURweAGPL7`)의 `지후니우스.pyw`를 방금 배포한 `dist/지후니우스.pyw`로 바꾼다(사용자 요청 2026-11-11). 커넥터가 본문을 덮어쓰지 못하므로 새 파일을 올리고 설명에 버전을 적은 뒤 이전 파일을 휴지통으로 옮겨, 폴더에는 최신 하나만 둔다. 드라이브에 연결할 수 없으면 그 사실을 사용자에게 알린다.
- 같은 폴더의 `지후니우스.exe`(아이콘 하나짜리 실행 파일. 사용자는 2026-11-26부터 이것으로 쓴다 — "exe도 올리면됨 앞으로 이걸로 쓸꺼")도 배포할 때마다 같은 방법으로 바꾼다: `python tools/build_launcher.py --app dist/지후니우스.pyw`로 만들어(mingw-w64 필요: `apt-get install gcc-mingw-w64-x86-64`) 올리고 설명에 안에 든 버전을 적은 뒤 이전 exe를 휴지통으로 옮긴다. 폴더에는 `.pyw`와 `.exe`가 최신 하나씩만 있게 한다. exe를 만들 수 없으면 이전 exe를 그대로 두고 그 사실을 사용자에게 알린다(안에 든 프로그램이 스스로 업데이트하므로 쓰는 데는 지장이 없다). exe는 저장소에 올리지 않는다(`build/`).
- 커밋 전: `python tools/build_app.py --check` 와 `python tools/run_tests.py`(전체 테스트를 파일 단위로 나눠 동시에 돌림, 약 1분. Linux의 가상 화면은 알아서 띄움). 작은 수정은 `python tools/run_tests.py <이름 일부>`로 관련 파일만 먼저 본다. 전체 테스트는 배포 한 번에 한 번이면 된다(배포본을 만든 뒤에는 `build_app.py --check`만). 한 줄로 돌리는 예전 방법 `python -m unittest discover -s tests -p 'test_*.py'`(Linux는 `xvfb-run -a -s "-screen 0 3840x1200x24"`)도 그대로 된다.
- 회사 PC는 Windows + Python 3.8 이상이다. 3.9 이상 전용 문법·외부 패키지를 쓰지 않는다.
- 소재 사용량 조사는 대표 보고 자료다. 집계·동기화 코드는 정확도 우선, 변경 시 관련 회귀 테스트를 넓힌다.
- 실적 DB, 연결 인증 값, 오류 원문은 저장소에 올리지 않는다.
- 작업기록은 사용자가 요청할 때만 남긴다. 위치는 Google Drive `작업기록/프로그램/지후니우스`이고(사용자 요청 2026-11-24), 쓰는 법은 그 폴더의 `00_정리규칙.txt`를 따른다: `00_최신요약.txt`는 지금 상태만 고쳐 쓰고 끝에 덧붙이지 않는다, `일별기록`은 날짜당 한 파일, 고쳐 쓰면서 물러난 파일은 `보관`으로 옮긴다.
