from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from .models import Profile, UserRole

class UserEditForm(forms.ModelForm):
    """Form for editing user's basic information"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'your.email@example.com'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'Enter your first name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'Enter your last name'
        })
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    def clean_email(self):
        email = self.cleaned_data['email']
        # Check if email is already taken by another user
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email

class ProfileEditForm(forms.ModelForm):
    """Form for editing user's profile information"""
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': '+256 XXX XXX XXX'
        })
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'Tell us about yourself, your interests in wildlife, and what makes you passionate about nature...',
            'rows': 4
        })
    )
    
    # Additional fields for different roles
    guide_experience_years = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'Years of experience as a guide'
        })
    )
    guide_languages = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'Languages you speak (comma-separated)'
        })
    )
    guide_specializations = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'Your specializations (e.g., wildlife, birding, cultural)'
        })
    )
    
    operator_company_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'Your tour company name'
        })
    )
    operator_license_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'Tour operator license number'
        })
    )
    operator_website = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'https://yourcompany.com'
        })
    )
    
    staff_employee_id = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'UWA Employee ID'
        })
    )
    staff_department = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'Your department at UWA'
        })
    )
    staff_position = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'Your job title/position'
        })
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Only allow role editing during signup or by UWA staff
        # Remove roles field from regular profile editing
        if 'roles' in self.fields:
            del self.fields['roles']

    class Meta:
        model = Profile
        fields = ('phone_number', 'bio', 'guide_experience_years', 'guide_languages', 
                 'guide_specializations', 'operator_company_name', 'operator_license_number', 
                 'operator_website', 'staff_employee_id', 'staff_department', 'staff_position')

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone:
            # Basic phone number validation
            import re
            phone_pattern = re.compile(r'^\+?[\d\s\-\(\)]+$')
            if not phone_pattern.match(phone):
                raise forms.ValidationError("Please enter a valid phone number.")
        return phone

class PasswordChangeForm(forms.Form):
    """Custom password change form"""
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'Enter your current password'
        })
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'Enter new password'
        })
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'Confirm new password'
        })
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError("Your old password was entered incorrectly. Please enter it again.")
        return old_password

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("The two password fields didn't match.")
        return password2

    def save(self, commit=True):
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user


class SignupForm(forms.ModelForm):
    """Enhanced signup form with role selection"""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 pl-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'Choose a unique username'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 pl-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'your.email@example.com'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 pl-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'Enter your first name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 pl-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'Enter your last name'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 pl-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'Create a strong password'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 pl-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': 'Confirm your password'
        })
    )
    roles = forms.ModelMultipleChoiceField(
        queryset=UserRole.objects.exclude(name='staff'),  # Exclude UWA staff from signup
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'roles-checkbox-list'
        }),
        required=True,
        help_text="Select your role(s). You can choose multiple roles if applicable. Note: UWA Staff roles are assigned by administrators only."
    )
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 pl-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
            'placeholder': '+256 XXX XXX XXX'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("The two password fields didn't match.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
            # Create profile and assign roles
            profile, created = Profile.objects.get_or_create(user=user)
            profile.phone_number = self.cleaned_data.get('phone_number', '')
            profile.save()
            profile.roles.set(self.cleaned_data['roles'])
        return user


class StaffUserManagementForm(forms.ModelForm):
    """Form for UWA staff to manage other users"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent'
        })
    )
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-5 w-5 text-safari-600 focus:ring-safari-500 border-gray-300 rounded'
        }),
        help_text="Uncheck to suspend the user account"
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_active')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent'
            })
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email


class StaffProfileManagementForm(forms.ModelForm):
    """Form for UWA staff to manage user profiles and roles"""
    roles = forms.ModelMultipleChoiceField(
        queryset=UserRole.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'roles-checkbox-list'
        }),
        required=False,
        help_text="Select all roles that apply to this user"
    )

    class Meta:
        model = Profile
        fields = ('roles', 'phone_number', 'bio', 'guide_experience_years', 'guide_languages', 
                 'guide_specializations', 'operator_company_name', 'operator_license_number', 
                 'operator_website', 'staff_employee_id', 'staff_department', 'staff_position')
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent',
                'rows': 4
            }),
            'guide_experience_years': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent'
            }),
            'guide_languages': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent'
            }),
            'guide_specializations': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent'
            }),
            'operator_company_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent'
            }),
            'operator_license_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent'
            }),
            'operator_website': forms.URLInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent'
            }),
            'staff_employee_id': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent'
            }),
            'staff_department': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent'
            }),
            'staff_position': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-safari-500 focus:border-transparent'
            }),
        }
