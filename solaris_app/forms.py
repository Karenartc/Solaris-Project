from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User
from django.core.exceptions import ValidationError
from itertools import cycle

class CreateUserForm(UserCreationForm):
    """
    Formulario para la creación de usuarios, extendiendo UserCreationForm.
    Incluye campos adicionales como email, first_name, last_name, username, rut, role, gender, age, address y phone_number.
    """
    email = forms.EmailField(
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'id': 'exampleInputEmail1', 'aria-describedby': 'emailHelp', 'required': True, 'placeholder': 'correo@example.com'})
    )
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'exampleInputPassword', 'required': True})
    )
    password2 = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'exampleInputConfirmPassword', 'required': True})
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'exampleInputFirstName', 'required': True}),
        label='Nombre'
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'exampleInputLastName', 'required': True}),
        label='Apellido'
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'exampleInputUsername', 'required': True}),
        label='Nombre de Usuario'
    )
    rut = forms.CharField(
        label='RUT',
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'exampleInputRut', 'required': True, 'placeholder': '13337687-9'})
    )
    role = forms.ChoiceField(
        label='Rol',
        choices=User.ROLES_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'exampleSelectRole', 'required': True})
    )
    gender = forms.ChoiceField(
        label='Género',
        choices=(('other', 'Otro'), ('male', 'Hombre'), ('female', 'Mujer')),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'exampleSelectGender', 'required': True})
    )
    age = forms.IntegerField(
        label='Edad',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'id': 'exampleInputAge', 'min': 0,
            'max': 120, 'required': True})
    )
    address = forms.CharField(
        label='Direción',
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'exampleInputAddress', 'required': True, 'placeholder': 'Calle Falsa 123'})
    )
    phone_number = forms.CharField(
        label='Número de Teléfono',
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'exampleInputPhoneNumber', 'required': True, 'placeholder': '952441697'})
    )

    def clean_rut(self):
        """
        Validación personalizada para el campo RUT.
        Verifica la estructura del RUT y su dígito verificador.
        """
        rut = self.cleaned_data.get('rut')
        rut = rut.replace('.', '').replace('-', '')

        if len(rut) < 2:
            raise ValidationError("El RUT ingresado no es válido.")
        
        # Divide el RUT en su parte numérica y su dígito verificador
        def calcular_digito_verificador(rut_num):
            reversed_digits = map(int, reversed(rut_num))
            factors = cycle(range(2, 8))
            s = sum(d * f for d, f in zip(reversed_digits, factors))
            dv = (-s) % 11
            return 'K' if dv == 10 else str(dv)
    
        rut_num, verif_digit = rut[:-1], rut[-1].upper()

        # Verifica que la parte numérica del RUT sea numérica
        if not rut_num.isdigit():
            raise ValidationError("El RUT ingresado no es válido.")

        # Calcula el dígito verificador esperado
        expected_verif_digit = calcular_digito_verificador(rut_num)

        # Compara el dígito verificador esperado con el proporcionado
        if verif_digit != expected_verif_digit:
            raise ValidationError("El dígito verificador del RUT no es válido.")
        
        return rut
    
    def clean_age(self):
        """
        Validación personalizada para el campo edad.
        Verifica que la edad esté en un rango válido y que el usuario sea mayor de edad.
        """
        age = self.cleaned_data.get('age')
        if age < 0 or age > 100:
            raise ValidationError("Por favor, introduce una edad válida entre 0 y 100 años.")
        if age < 18:
            raise ValidationError("Debes ser mayor de edad para registrarte.")
        return age

    def clean_phone_number(self):
        """
        Validación personalizada para el campo número de teléfono.
        Verifica que el número tenga 9 dígitos y que comience con 9.
        """
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.isdigit() or len(phone_number) != 9 and not phone_number.startswith('9'):
            raise ValidationError("Por favor, introduce un número de teléfono válido de 9 dígitos y que empiece con 9.")
        return phone_number
    
    def clean_email(self):
        """
        Validación personalizada para el campo email.
        Verifica que el correo electrónico no esté registrado en otro usuario.
        """
        email = self.cleaned_data.get('email')
        if self.instance and self.instance.pk:
            if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise ValidationError("Este correo electrónico ya está registrado. Por favor, utiliza otro.")
        else:
            if User.objects.filter(email=email).exists():
                raise ValidationError("Este correo electrónico ya está registrado. Por favor, utiliza otro.")
        return email

    def clean_username(self):
        """
        Validación personalizada para el campo nombre de usuario.
        Verifica que el nombre de usuario no esté registrado en otro usuario.
        """
        username = self.cleaned_data.get('username')
        if self.instance and self.instance.pk:
            if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
                raise ValidationError("Este nombre de usuario ya está registrado. Por favor, utiliza otro.")
        else:
            if User.objects.filter(username=username).exists():
                raise ValidationError("Este nombre de usuario ya está registrado. Por favor, utiliza otro.")
        return username


    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'rut', 'email', 'password1', 'password2', 'role', 'gender', 'age', 'address', 'phone_number']

class PasswordResetForm(forms.Form):
    """
    Formulario para la solicitud de restablecimiento de contraseña.
    Incluye el campo de correo electrónico.
    """
    email = forms.EmailField(label='Correo Electrónico', max_length=254, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'name@example.com'
    }))

class CodeVerificationForm(forms.Form):
    """
    Formulario para la verificación del código de restablecimiento de contraseña.
    Incluye el campo para el código.
    """
    code = forms.CharField(label='Código de verificación', max_length=5, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Código de verificación'
    }))

class SetPasswordForm(forms.Form):
    """
    Formulario para establecer una nueva contraseña después de la verificación del código.
    Incluye los campos para la nueva contraseña y su confirmación.
    """
    new_password = forms.CharField(label='Nueva Contraseña', widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Nueva Contraseña'
    }))
    confirm_password = forms.CharField(label='Confirmar Nueva Contraseña', widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirmar Nueva Contraseña'
    }))

    def clean(self):
        """
        Validación personalizada para asegurarse de que las contraseñas coincidan.
        """
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Las contraseñas no coinciden.")

