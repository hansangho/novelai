# 장르 프리셋

`/init-novel <장르>` 로 미리 채워진 Bible 시작점.

## 포함된 장르
| ID | 설명 |
|----|------|
| `historic-noir` | 1900~1950 시대극 + 누아르 (느와르 톤·당대 어휘) |
| `urban-fantasy` | 현대 한국 + 초자연 (능력 비용·일관성 중시) |
| `web-novel`     | 웹소설 (회귀·헌터·로판) — 짧은 문장·빠른 템포·후킹 |
| `sf`            | 하드 SF·스페이스 오페라 (기술 일관성·트로프 변주) |

## 사용
```
/init-novel historic-noir
```

지정한 장르의 `style-rules.json` / `structure.md` / `characters/_template.md` (있으면) 가 기본 템플릿 위에 덮어 씌워집니다. 기본 템플릿이 먼저 깔리고, 장르 프리셋이 그 위에 추가·교체.

## 새 장르 추가
플러그인 개발자가 `templates/genres/<id>/` 디렉토리를 추가하면 자동 인식. README + style-rules.json 권장.

## extends 작동
각 장르의 `style-rules.json` 의 `_extends` 필드가 기본 룰을 가리킴. Style Linter 는 두 파일을 합쳐 적용 (장르 규칙이 우선).
