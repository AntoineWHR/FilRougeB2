from yops_portal.core.web import YOpsApplication


if __name__ == "__main__":
    app = YOpsApplication(host="127.0.0.1", port=8000)
    app.run()

