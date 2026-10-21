SELECT user_id, login, user_group, full_name
  FROM internal_user
 WHERE login = %(login)s
   AND password = %(password)s;
