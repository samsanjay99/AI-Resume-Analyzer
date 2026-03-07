
import streamlit as st

# Custom HTML/CSS
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def main():
    st.markdown('''
        <div class="container">
            <div class="bird"></div>
            <div class="form-box">
                <form>
                    <h2>Login Form</h2>
                    <div class="input-box">
                        <span class="icon"><ion-icon name="mail"></ion-icon></span>
                        <input type="email" required>
                        <label>Enter your email</label>
                    </div>
                    <div class="input-box">
                        <span class="icon"><ion-icon name="lock-closed"></ion-icon></span>
                        <input type="password" required>
                        <label>Enter your password</label>
                    </div>
                    <div class="group">
                        <div>
                            <input type="checkbox" id="remember-me">
                            <label for="remember-me">Remember me</label>
                        </div>
                        <a href="#">Forgot password?</a>
                    </div>
                    <button type="submit">Log In</button>
                    <div class="register-link">
                        <p>Don't have an account? <a href="#">Register</a></p>
                    </div>
                </form>
            </div>
        </div>
    ''', unsafe_allow_html=True)

if __name__ == "__main__":
    main()

