# Update Origin File Implementation Plan

**Goal:** 적용된 최신 버전을 실행 경로의 원본 파일에도 반영한다.
**Architecture:** 검증된 캐시 실행본의 시작 완료 후 원본 교체 작업을 별도 제한시간 프로세스로 실행한다. 기존 로컬 버전 선택과 업데이트 전 저장 순서는 유지한다.
**Tech Stack:** Python 3.8+, Tk, 기존 FileLock/atomic/SHA256 검증.
**Spec:** ../specs/2026-11-09-update-origin-design.md

## Constraints and review focus
- 새 원본 시작 확인 전 교체 금지. 다운로드/취소/부팅 실패만으로는 원본 변경 금지.
- 공유 잠금, 더 높은 버전/알 수 없는 변경/동일 버전 해시 충돌 보호.
- 원본 쓰기 실패/느린 공유가 업무 UI를 멈추지 않아야 한다.
- 현재 실행기의 원본 경로를 사용하고 설정/업무 파일을 변경하지 않는다.
- 기존 구 실행기에서의 최초 업데이트에도 동작해야 한다.

## Tasks
- [ ] src/update_origin.py: source_version(data), replace_origin(origin, candidate, payload, known_hashes), sync_origin_bounded(context), origin_worker(source). 실제 파일 교체/백업/동시 잠금/최신 보호/실패/준비 미완료 시험을 먼저 작성해 실패 확인 후 구현.
- [ ] src/update_ui.py: 시작 확인 이후 한 번 동기화, 상태 표시 및 수동 다시 확인 재시도. tests/test_update_origin_ui.py로 기존 검사/다운로드/취소와 분리 확인.
- [ ] tools/prepare_release.py: engine+origin+UI 내장. 새 .3 파일 생성. 실제 배포 파일의 작업 프로세스 실행 시험 및 test_engine/test_update_apply/test_update_notice/test_release_package/test_program_paths 검증.
- [ ] 전체 변경 검토 후 준비 브랜치에 저장하고 파일 제공. 정식 main 배포/Drive 기록 갱신은 이번 범위에서 제외.

진행 판단: 사용자 요청이 원본도 최신으로 교체하는 동작을 명시했고 기존 구성 보존/시간 단축을 요구하므로 별도 설계 승인 질문 없이 이 범위로 진행한다. 네트워크 공유 변경은 실사용 프로그램이 업데이트 적용할 때 수행하며 개발 환경에서 회사 원본에 접근하지 않는다.
