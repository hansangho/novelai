# 역사 느와르 프리셋

이 디렉토리는 `/init-novel historic-noir` 시 복사되는 장르별 시작점.

## 포함 파일
- `style-rules.json` — 기본 룰 + 느와르 톤 추가 규칙 (짧은 호흡·당대 어휘 권장)
- `structure.md` — 25 챕터 표준 블록·서브플롯·금지선·레퍼런스
- `characters/_template.md` — 느와르 캐릭터 템플릿 (도덕적 타협한 과거·지식 경계 강화)

## 사용
```
/init-novel historic-noir
```

또는 init 후 수동으로 복사:
```bash
cp -r ${CLAUDE_PLUGIN_ROOT}/templates/genres/historic-noir/* bible/
```

## 적용된 장르 권장
- 1900~1950 시대극 (한국·중국·일본·동아시아)
- 첩보·범죄·미스터리
- 가족·과거의 그림자가 핵심 모티프
