# 지후니우스 작업 규칙 (AI·사람 공통)

- `apps/jihunius/app.pyw`, `dist/`, `releases/`는 **빌드 결과물**이다. 직접 고치지 말고 `src/`·`assets/`를 고친 뒤 `python tools/build_app.py`로 만든다. 구조는 README의 "소스 구조와 빌드" 참고.
- 기존 기능은 **온전히** 유지한다. 속도 개선·디자인 변경도 기능 동작을 바꾸면 안 된다.
- 배포 = `main`의 `channels/stable.json` 변경이다. 사용자가 "배포해줘"라고 할 때만 `tools/prepare_release.py`로 새 버전을 만들어 main에 올린다. 그 외 작업은 작업 브랜치에서 한다.
- 이미 올린 `releases/jihunius/<버전>/`은 절대 덮어쓰지 않는다.
- 커밋 전: `python tools/build_app.py --check` 와 `python -m unittest discover -s tests -p 'test_*.py'` (Linux는 `xvfb-run -a -s "-screen 0 3840x1200x24"`로 실행).
- 회사 PC는 Windows + Python 3.8 이상이다. 3.9 이상 전용 문법·외부 패키지를 쓰지 않는다.
- 소재 사용량 조사는 대표 보고 자료다. 집계·동기화 코드는 정확도 우선, 변경 시 관련 회귀 테스트를 넓힌다.
- 실적 DB, 연결 인증 값, 오류 원문은 저장소에 올리지 않는다.
- 작업기록(Google Drive `작업기록/프로그램`)은 사용자가 요청할 때만 남긴다.
