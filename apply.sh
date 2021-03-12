# copy all style content to VP
echo "copying $VP_THEME_HOME/style content to $VP_HOME/vocprez/view/style"
cp $VP_THEME_HOME/style/* $VP_HOME/vocprez/view/style

# copy all templates to VP
echo "copying $VP_THEME_HOME/templates content to $VP_HOME/vocprez/view/templates"
cp $VP_THEME_HOME/templates/* $VP_HOME/vocprez/view/templates

# copy source
echo "copying $VP_THEME_HOME/source content to $VP_HOME/vocprez/source"
cp $VP_THEME_HOME/source/* $VP_HOME/vocprez/source

# alter app.py
sed -n '/# ROUTE index/q;p' $VP_HOME/vocprez/app.py > $VP_THEME_HOME/app_temp.py
cat $VP_THEME_HOME/app_additions.py >> $VP_THEME_HOME/app_temp.py
sed -e '1,/# END ROUTE index/ d' $VP_HOME/vocprez/app.py >> $VP_THEME_HOME/app_temp.py
sed -i 's/c = source.SPARQL(request).get_collection(uri)/c = source.OGCSPARQL(request).get_collection(uri)/' $VP_THEME_HOME/app_temp.py
mv $VP_THEME_HOME/app_temp.py $VP_HOME/vocprez/app.py

echo "Config"
echo "creating VocPrez config with $VP_THEME_HOME/config.py"
echo "Alter config.py to include variables"
sed 's#$SPARQL_ENDPOINT#'"$SPARQL_ENDPOINT"'#' $VP_THEME_HOME/config.py > $VP_THEME_HOME/config_updated.py
if [ -z "$SPARQL_USERNAME" ]
then
      sed -i 's#$SPARQL_USERNAME#None#' $VP_THEME_HOME/config_updated.py
else
      sed -i 's#$SPARQL_USERNAME#'\"$SPARQL_USERNAME\"'#' $VP_THEME_HOME/config_updated.py
fi
if [ -z "$SPARQL_PASSWORD" ]
then
      sed -i 's#$SPARQL_PASSWORD#None#' $VP_THEME_HOME/config_updated.py
else
      sed -i 's#$SPARQL_PASSWORD#'\"$SPARQL_PASSWORD\"'#' $VP_THEME_HOME/config_updated.py
fi
mv $VP_THEME_HOME/config_updated.py $VP_HOME/vocprez/_config/__init__.py

echo "customisation done"