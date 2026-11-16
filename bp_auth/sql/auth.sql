SELECT user_id, login, user_group, full_name, password
  FROM internal_user
 WHERE login = %(login)s
