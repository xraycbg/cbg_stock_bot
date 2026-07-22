import requests
import json
import base64
import os
from dotenv import load_dotenv

# 로컬 환경 변수 로드
load_dotenv()

class GitHubDB:
    def __init__(self, token=None, repo=None, file_path=None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.repo = repo or os.getenv("GITHUB_REPO")
        self.file_path = file_path or os.getenv("GITHUB_FILE_PATH", "state.json")
        
        # API 호출용 기본 URL 및 헤더 설정
        self.base_url = f"https://api.github.com/repos/{self.repo}/contents/{self.file_path}"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def get_state(self):
        """
        깃허브 레포지토리에서 state.json 파일을 다운로드하여 딕셔너리로 반환합니다.
        파일이 없거나 오류가 발생하면 기본값을 생성하여 반환합니다.
        """
        try:
            res = requests.get(self.base_url, headers=self.headers)
            if res.status_code == 200:
                data = res.json()
                sha = data["sha"]
                # base64 디코딩
                content_bytes = base64.b64decode(data["content"])
                content_str = content_bytes.decode("utf-8")
                state = json.loads(content_str)
                return state, sha
            elif res.status_code == 404:
                # 파일이 없을 경우 기본 템플릿 반환
                print("state.json 파일이 존재하지 않아 새로운 템플릿을 생성합니다.")
                default_state = self._get_default_state()
                return default_state, None
            else:
                raise Exception(f"GitHub API Error: {res.status_code} - {res.text}")
        except Exception as e:
            print(f"상태를 불러오는 중 오류 발생: {e}")
            # 로컬 예비 템플릿 읽기 시도
            try:
                with open("state_template.json", "r", encoding="utf-8") as f:
                    return json.load(f), None
            except:
                return self._get_default_state(), None

    def update_state(self, new_state, sha=None):
        """
        새로운 상태(new_state)를 JSON으로 변환하여 깃허브 레포지토리에 저장합니다.
        기존 파일의 sha 값이 필요하지만, 없을 경우 또는 SHA 불일치 시 자동으로 최신 SHA를 로드합니다.
        """
        content_str = json.dumps(new_state, indent=2, ensure_ascii=False)
        content_bytes = content_str.encode("utf-8")
        content_b64 = base64.b64encode(content_bytes).decode("utf-8")
        
        # 항상 최신 sha 조회 시도
        if not sha:
            _, fetched_sha = self.get_state()
            sha = fetched_sha

        payload = {
            "message": "Update trading state via stock bot",
            "content": content_b64
        }
        if sha:
            payload["sha"] = sha

        res = requests.put(self.base_url, headers=self.headers, data=json.dumps(payload))
        if res.status_code in [200, 201]:
            print("성공적으로 state.json 상태가 깃허브에 업데이트되었습니다.")
            return True, res.json()["content"]["sha"]
        else:
            # SHA 불일치 (409/422 등) 발생 시 최신 SHA로 자동 1회 재시도
            print(f"상태 감지 SHA 재동기화 시도 (상태코드: {res.status_code})")
            _, latest_sha = self.get_state()
            if latest_sha:
                payload["sha"] = latest_sha
                retry_res = requests.put(self.base_url, headers=self.headers, data=json.dumps(payload))
                if retry_res.status_code in [200, 201]:
                    print("SHA 재동기화 성공 후 저장되었습니다.")
                    return True, retry_res.json()["content"]["sha"]
            print(f"상태 업데이트 실패: {res.status_code} - {res.text}")
            return False, sha


    def _get_default_state(self):
        """기본 상태 딕셔너리를 반환합니다."""
        return {
            "target_etf": "TQQQ",
            "total_budget": 10000.0,
            "splits": 40,
            "turn": 0,
            "avg_price": 0.0,
            "total_shares": 0.0,
            "total_spent": 0.0,
            "status": "BUYING",
            "history": []
        }

if __name__ == "__main__":
    # 로컬 테스트용
    db = GitHubDB()
    state, sha = db.get_state()
    print("현재 상태:", state)
    print("현재 SHA:", sha)
