import pymysql
import daytime
import sys

class Grade_management_programe:
    def __init__(self):
        self.DB_HOST = "127.0.0.1"
        self.DB_PASS = "security"
        self.DB_USER = "root"
        self.DB_PORT = 3307
        self.DB_NAME = "cju"

    def connect_db(self):
        return pymysql.connect(
            host=self.DB_HOST,
            user=self.DB_USER,
            password=self.DB_PASS,
            db=self.DB_NAME,
            port=self.DB_PORT,
            charset='utf8mb4'
        )

    def main(self):
        while True:
            print("\n--- [ 성적 관리 시스템 ] ---")
            print("1. 전체조회")
            print("2. 번호조회")
            print("3. 데이터 추가")
            print("4. 데이터 삭제")
            print("5. 성적 수정")
            print("6. 종료")

            choice = input("메뉴 선택: ")

            if choice == '1':
                self.select_all()
            elif choice == '2':
                self.select_one()
            elif choice == '3':
                self.insert_member()
            elif choice == '4':
                self.delete_member()
            elif choice == '5':
                self.update_member()
            elif choice == '6':
                print("프로그램이 종료되었습니다. 감사합니다.")
                break
            else:
                print("잘못된 선택입니다. 다시 입력하시기 바랍니다.")

    def select_all(self):
        try:
            conn = self.connect_db()
            cursor = conn.cursor()

            sql = """
            SELECT m.seq, m.name, m.id, g.subject, g.score, g.term, g.reg_date
            FROM member m
            JOIN grades g ON m.seq = g.member_seq
            """

            cursor.execute(sql)
            results = cursor.fetchall()

            print("\n--- [ 성적 전체 목록 ] ---")
            print("번호 | 이름(ID)    | 과목명            | 점수 | 학기   | 등록일")
            print("-----------------------------------------------------------")

            count = 0
            for row in results:
                seq, name, user_id, subject, score, term, reg_date = row

                print(f"{seq:<4} | {name}({user_id}) | {subject:<15} | {score:<3} | {term:<6} | {reg_date}")
                count += 1

            print("-----------------------------------------------------------")
            print(f"(총 {count}건의 성적이 조회되었습니다.)")

            cursor.close()
            conn.close()

        except Exception as e:
            print(e)

    def select_one(self):
        try:
            seq = input("조회할 학생 번호(seq) 입력: ")

            conn = self.connect_db()
            cursor = conn.cursor()

            sql = """
            SELECT m.name, m.id, g.subject, g.score, g.term
            FROM member m
            JOIN grades g ON m.seq = g.member_seq
            WHERE m.seq = %s
            """

            cursor.execute(sql, (seq,))
            results = cursor.fetchall()

            if not results:
                print("해당 학생이 존재하지 않습니다.")
                return

            # 공통 정보 추출 (첫 행 기준)
            name = results[0][0]
            user_id = results[0][1]
            term = results[0][4]

            print(f"\n--- [ {name} 학생의 성적 리포트 ] ---")
            print(f"- 아이디: {user_id}")
            print(f"- 학기: {term}")
            print("---------------------------")

            total = 0
            count = 0

            for i, row in enumerate(results, start=1):
                subject = row[2]
                score = row[3]

                print(f"{i}. {subject}: {score}점")

                total += score
                count += 1

            print("---------------------------")

            avg = total / count
            print(f"평균 점수: {avg:.1f}점")

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"ERROR: {e}")
        
    def insert_member(self):
        try:
            name = input("이름: ")
            user_id = input("아이디: ")
            user_pass = input("비밀번호: ")
            subject = input("과목: ")
            score = int(input("점수: "))
            term = input("학기: ")

            conn = self.connect_db()
            cursor = conn.cursor()

            cursor.execute("SELECT MAX(seq) FROM member")
            result = cursor.fetchone()

            if result[0] is None:
                new_seq = 1
            else:
                new_seq = result[0] + 1

            cursor.execute(
                "INSERT INTO member (seq, id, pass, name) VALUES (%s,%s,%s,%s)",
                (new_seq, user_id, user_pass, name)
            )

            cursor.execute(
                "INSERT INTO grades (member_seq, subject, score, term) VALUES (%s,%s,%s,%s)",
                (new_seq, subject, score, term)
            )

            conn.commit()
            conn.close()

            print("데이터 추가 완료")
            print(f"[시스템] {name} 학생의 {subject} 성적이 성공적으로 등록되었습니다. ")

        except Exception as e:
            print(f"ERROR : {e}")

    def delete_member(self):
        try:
            seq = input("삭제할 성적의 고유 ID를 입력하세요. : ")
            


            conn = self.connect_db()
            cursor = conn.cursor()
            answer = input("정말로 삭제하겠습니까?: ")
            if answer == "y":
                cursor.execute("DELETE FROM member WHERE seq=%s", (seq,))
                print("[시스템] 5번 성적 데이터가 삭제되었습니다.")
            else:
                sys.exit(1)
            conn.commit()
            conn.close()
            print("삭제가 완료되었습니다.")
            
        except Exception as e:
            print(f"ERROR: {e}")

    def update_member(self):
        try:
            grade_id = input("수정할 성적의 고유 ID(id_grade) 입력: ")

            conn = self.connect_db()
            cursor = conn.cursor()

            #기존 결과 조회 
            cursor.execute(
                "SELECT subject, score FROM grades WHERE id_grade=%s",
                (grade_id,)
            )
            result = cursor.fetchone()

            if not result:
                print("해당 성적이 존재하지 않습니다.")
                return

            subject, old_score = result

            print(f"--- 현재 정보: {subject} ({old_score}점) ---")

            new_score = int(input("- 수정할 점수 입력: "))

      
            cursor.execute(
                "UPDATE grades SET score=%s WHERE id_grade=%s",
                (new_score, grade_id)
            )

            conn.commit()
            conn.close()

            
            print(f"\n[시스템] 성적 수정이 완료되었습니다. ({old_score}점 -> {new_score}점)")

        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    programe = Grade_management_programe()
    programe.main()
