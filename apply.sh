# copy all style content to VP
echo "copying $VP_THEME_HOME/style content to $VP_HOME/vocprez/view/style"
cp $VP_THEME_HOME/style/* $VP_HOME/vocprez/view/style

# copy all templates to VP
echo "copying $VP_THEME_HOME/templates content to $VP_HOME/vocprez/view/templates"
cp $VP_THEME_HOME/templates/* $VP_HOME/vocprez/view/templates

# alter app.py
echo "replacing index() in $VP_HOME/vocprez/app.py"
start_line=$(grep -n "# ROUTE index" $VP_HOME/vocprez/app.py | head -n 1 | cut -d: -f1)
start_line=$((start_line -1))
head -$start_line $VP_HOME/vocprez/app.py > test.py

more app_additions.py >> test.py

end_line=$(grep -n "# END ROUTE index" $VP_HOME/vocprez/app.py | head -n 1 | cut -d: -f1)
end_line=$((end_line + 2))
tail -n +$end_line $VP_HOME/vocprez/app.py >> test.py

rm $VP_HOME/vocprez/app.py
mv test.py $VP_HOME/vocprez/app.py

echo "customisation done"