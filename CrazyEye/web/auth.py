#Authon Ivor
#_*_coding:utf-8_*_

from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser,Group,PermissionsMixin
)
#自定义用户认证创建用户时引用的Form
class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name ,password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(email,
            password=password,
            name=name,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user