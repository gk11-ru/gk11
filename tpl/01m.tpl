<div class="top-bar">
  <div class="top-bar-title">
    <span data-responsive-toggle="responsive-menu" data-hide-for="medium">
      <button class="menu-icon dark" type="button" data-toggle></button>
    </span>
  </div>
<div id="responsive-menu">
<div class="top-bar-left">
<ul class="menu">
<li class="menu-text">:{{ea}}</li>

            <li><a href="/l/{{ea}}/{{page}}{{',100,intrev' if opts[2]!='intrev' else ''}}" title="От старых к новым" {{! 'class="alert button"' if opts[2] == 'intrev' else ''}}><i class="fa fa-sort-numeric-asc "></i></a></li>
            <li><a href="/rss/{{ea}}" title="RSS-лента"><i class="fa fa-fw fa-rss" style="color:orange"></i></a></li>
	    <li><a href="/:{{ea}}" title="Обновить страницу"><i class="fa fa-fw fa-refresh"></i></a></li>
            <li><a href="/lite/{{ea}}" title="Plain HTML version"><i class="fa fa-fw fa-file-text-o"></i></a></li>
            <li><a href="/reply/{{ea}}/-" title="Написать новое сообщение в эту эху">
                <i class="fa fa-plus-circle"></i> Новое сообщение</a>
            </li>

</ul>
</div>
<div class="top-bar-right">
<ul class="menu">
<li><a href="/user/me">{{! '<i class="fa fa-user"></i>' + _escape(u.uname) if u else '<i class="fa fa-fw fa-key"></i> LOGIN'}}</a></li>
<li><a href="/"><i class="fa fa-home"></i>Главная</a></li>
</ul>
</div>
</div>
</div>
