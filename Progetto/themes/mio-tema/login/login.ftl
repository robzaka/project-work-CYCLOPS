<!doctype html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <title>Login - ${realm.displayName!''}</title>
  <link rel="stylesheet" href="${url.resourcesPath}/css/style.css">
</head>
<body>

<header>
  <div>CYCLOPS</div>
</header>

<main>
  <h1>Accedi</h1>
  <p><em>Effettua il login per continuare.</em></p>

  <#if message?has_content>
    <div class="error">${message.summary}</div>
  </#if>

  <form id="kc-form-login" action="${url.loginAction}" method="post">
    <input tabindex="1" id="username" name="username" type="text" placeholder="Username o Email" autofocus autocomplete="username" value="${login.username!''}"/>
    <input tabindex="2" id="password" name="password" type="password" placeholder="Password" autocomplete="current-password"/>
    <input tabindex="3" name="login" type="submit" value="Accedi"/>
  </form>

  <#if realm.resetPasswordAllowed>
    <p><a href="${url.loginResetCredentialsUrl}">Hai dimenticato la password?</a></p>
  </#if>
</main>

</body>
</html>
