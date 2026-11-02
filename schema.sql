-- Supabase SQL Editor에서 실행 (앱 시작 시에도 자동 생성되므로 선택 사항)
CREATE TABLE IF NOT EXISTS todos (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    priority TEXT NOT NULL DEFAULT 'medium',
    due_date TEXT,
    done INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 앱은 서버(postgres 역할)로만 접속하므로, 공개 API(anon 키)로는 접근 못 하게 RLS 활성화
ALTER TABLE todos ENABLE ROW LEVEL SECURITY;
