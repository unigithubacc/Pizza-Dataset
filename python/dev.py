from streamlit.web import bootstrap


def main():
    real_script = 'app.py'

    bootstrap.run(real_script, f'run.py {real_script}', [], {})


if __name__ == "__main__":
    main()