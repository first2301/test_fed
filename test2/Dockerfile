FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# 패키지 설치 (apt-get update와 install을 한 번에 묶는 것이 캐싱/용량 관리에 유리함)
RUN apt-get update && apt-get install -y \
    openssh-server \
    python3 \
    python3-pip \
    python3-venv \
    iputils-ping \
    curl \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# 가상환경 설정
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Python 패키지 설치
RUN pip install --upgrade pip setuptools wheel 
RUN pip install flwr[simulation]>=1.23.0 \
    flwr-datasets[vision]>=0.5.0 \
    scikit-learn>=1.6.1

# 작업 디렉토리 생성
RUN mkdir -p /root/distributed

# SSH 설정
RUN mkdir -p /var/run/sshd
RUN ssh-keygen -A

# SSH 접속 허용 설정
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    sed -ri 's/UsePAM yes/#UsePAM yes/g' /etc/ssh/sshd_config

# 🚨 주의: 비밀번호는 'password'입니다. 외부(0.0.0.0) 포트 개방 금지!
RUN echo 'root:password' | chpasswd

# [변경점] 별도의 start.sh 스크립트 없이 SSH 데몬을 직접 실행
# -D 옵션: 데몬을 백그라운드가 아닌 포그라운드로 실행하여 컨테이너가 꺼지지 않게 함
# -e 옵션: 로그를 표준 오류(stderr)로 출력하여 'docker logs'로 확인 가능하게 함
CMD ["/usr/sbin/sshd", "-D", "-e"]