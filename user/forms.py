from django import forms
from django.contrib import auth
from django.contrib.auth.models import User
from .models import OAuthRelationship

class LoginForm(forms.Form):
    username_or_email = forms.CharField(
        label='username or email address', 
        widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Please enter a username or email'})
    )
    password = forms.CharField(label='password', 
                               widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Please enter a password'}))

    def clean(self):
        username_or_email = self.cleaned_data['username_or_email']
        password = self.cleaned_data['password']

        user = auth.authenticate(username=username_or_email, password=password)
        if user is None:
            if User.objects.filter(email=username_or_email).exists():
                username = User.objects.get(email=username_or_email).username
                user = auth.authenticate(username=username, password=password)
                if not user is None:
                    self.cleaned_data['user'] = user
                    return self.cleaned_data
            raise forms.ValidationError('Username or password is incorrect')
        else:
            self.cleaned_data['user'] = user
        return self.cleaned_data

class RegForm(forms.Form):
    username = forms.CharField(
        label='Username', 
        max_length=30,
        min_length=3,
        widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Please enter 3-30 usernames'})
    )
    email = forms.EmailField(
        label='email', 
        widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder':'email'})
    )
    verification_code = forms.CharField(
        label='Captcha',
        required=False,
        widget=forms.TextInput(
            attrs={'class':'form-control', 'placeholder':'Click "Send Verification Code" to send to the mailbox'}
        )
    )
    password = forms.CharField(
        label='password', 
        min_length=6,
        widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'password'})
    )
    password_again = forms.CharField(
        label='Enter the password again', 
        min_length=6,
        widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Enter the password again'})
    )

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(RegForm, self).__init__(*args, **kwargs)

    def clean(self):
        # Verification code
        code = self.request.session.get('register_code', '')
        verification_code = self.cleaned_data.get('verification_code', '')
        if not (code != '' and code == verification_code):
            raise forms.ValidationError('Incorrect verification code')
        return self.cleaned_data

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already exists')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Mailbox already exists')
        return email

    def clean_password_again(self):
        password = self.cleaned_data['password']
        password_again = self.cleaned_data['password_again']
        if password != password_again:
            raise forms.ValidationError('Passwords entered twice are inconsistent')
        return password_again

    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code', '').strip()
        if verification_code == '':
            raise forms.ValidationError('verification code must be filled')
        return verification_code

class ChangeNicknameForm(forms.Form):
    nickname_new = forms.CharField(
        label='New nickname', 
        max_length=20,
        widget=forms.TextInput(
            attrs={'class':'form-control', 'placeholder':'Please enter a new nickname'}
        )
    )

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(ChangeNicknameForm, self).__init__(*args, **kwargs)

    def clean(self):
        # 判断用户是否登录
        if self.user.is_authenticated:
            self.cleaned_data['user'] = self.user
        else:
            raise forms.ValidationError('User has not logged in')
        return self.cleaned_data

    def clean_nickname_new(self):
        nickname_new = self.cleaned_data.get('nickname_new', '').strip()
        if nickname_new == '':
            raise forms.ValidationError("The new nickname cannot be empty")
        return nickname_new

class BindEmailForm(forms.Form):
    email = forms.EmailField(
        label='mailbox',
        widget=forms.EmailInput(
            attrs={'class':'form-control', 'placeholder':'please enter your vaild email'}
        )
    )
    verification_code = forms.CharField(
        label='Captcha',
        required=False,
        widget=forms.TextInput(
            attrs={'class':'form-control', 'placeholder':'Click "Send Verification Code" to send to the mailbox'}
        )
    )

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(BindEmailForm, self).__init__(*args, **kwargs)

    def clean(self):
        # 判断用户是否登录
        if self.request.user.is_authenticated:
            self.cleaned_data['user'] = self.request.user
        else:
            raise forms.ValidationError('User has not logged in')

        # 判断用户是否已绑定邮箱
        if self.request.user.email != '':
            raise forms.ValidationError('You have bound your mailbox')

        # 判断验证码
        code = self.request.session.get('bind_email_code', '')
        verification_code = self.cleaned_data.get('verification_code', '')
        if not (code != '' and code == verification_code):
            raise forms.ValidationError('Incorrect verification code')

        return self.cleaned_data

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('The mailbox is already bound')
        return email

    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code', '').strip()
        if verification_code == '':
            raise forms.ValidationError('verification code must be filled')
        return verification_code

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        label='Old password', 
        widget=forms.PasswordInput(
            attrs={'class':'form-control', 'placeholder':'Please enter the old password'}
        )
    )
    new_password = forms.CharField(
        label='New password', 
        widget=forms.PasswordInput(
            attrs={'class':'form-control', 'placeholder':'Please enter a new password'}
        )
    )
    new_password_again = forms.CharField(
        label='Please enter the new password again', 
        widget=forms.PasswordInput(
            attrs={'class':'form-control', 'placeholder':'Please enter the new password again'}
        )
    )

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean(self):
        # 验证新的密码是否一致
        new_password = self.cleaned_data.get('new_password', '')
        new_password_again = self.cleaned_data.get('new_password_again', '')
        if new_password != new_password_again or new_password == '':
            raise forms.ValidationError('Passwords entered twice are inconsistent')
        return self.cleaned_data

    def clean_old_password(self):
        # 验证旧的密码是否正确
        old_password = self.cleaned_data.get('old_password', '')
        if not self.user.check_password(old_password):
            raise forms.ValidationError('Old password is wrong')
        return old_password

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        label='mailbox',
        widget=forms.EmailInput(
            attrs={'class':'form-control', 'placeholder':'Please enter the bound email'}
        )
    )
    verification_code = forms.CharField(
        label='Captcha',
        required=False,
        widget=forms.TextInput(
            attrs={'class':'form-control', 'placeholder':'Click "Send Verification Code" to send to the mailbox'}
        )
    )
    new_password = forms.CharField(
        label='New password', 
        widget=forms.PasswordInput(
            attrs={'class':'form-control', 'placeholder':'Please enter a new password'}
        )
    )

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(ForgotPasswordForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('Mailbox does not exist')
        return email

    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code', '').strip()
        if verification_code == '':
            raise forms.ValidationError('verification code must be filled')

        # 判断验证码
        code = self.request.session.get('forgot_password_code', '')
        verification_code = self.cleaned_data.get('verification_code', '')
        if not (code != '' and code == verification_code):
            raise forms.ValidationError('Incorrect verification code')

        return verification_code

class BindQQForm(forms.Form):
    username_or_email = forms.CharField(
        label='username or email address', 
        widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Please enter a username or email'})
    )
    password = forms.CharField(label='password', 
                               widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Please enter the password'}))

    def clean(self):
        username_or_email = self.cleaned_data['username_or_email']
        password = self.cleaned_data['password']

        user = auth.authenticate(username=username_or_email, password=password)
        if user is None:
            if User.objects.filter(email=username_or_email).exists():
                username = User.objects.get(email=username_or_email).username
                user = auth.authenticate(username=username, password=password)
                if not user is None:
                    self.cleaned_data['user'] = user
                    return self.cleaned_data
            raise forms.ValidationError('Username or password is incorrect')
        else:
            self.cleaned_data['user'] = user

        if OAuthRelationship.objects.filter(user=user, oauth_type=0).exists():
            raise forms.ValidationError('The user has bound QQ account')
        return self.cleaned_data