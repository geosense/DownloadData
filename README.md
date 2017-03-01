Cleerio Data Download QGIS Plugin
=================================


Translation
-----------

1. In the source code, use `QtGui.QDialog.tr` function.

2. Go to `i18n` directory and run

```
cd i18n
pyside-lupdate -verbose download_data.pro 
lupdate -verbose download_data.pro 
```

3. Open QT Linguist and translate what is to be translated - all `*.ts` files
   being created

4. After translation is finished, run `lrelease`

```
lrelease *.ts
```
5. When you change something in GUI or in `download_data_dialog.py`, you have to
   repeat all steps

6. Git commit && git push

```
git commit -m"Translation updated" *.ts *.qm`
```
