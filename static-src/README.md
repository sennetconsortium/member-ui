# Client Side Static Source Files
Facilitates building of custom plugins and JS apps that can be shared across templates and/or pages.

## JS 
### Install 
```
cd static-src
npm i .
```
### Development
This will watch all `.coffee` files and build to `static/js/app.min.js`
```
npm run dev
```
Currently just minifies the js to `static/js/app.min.js`
```
npm run build
```

For building select files, run:
```
coffee --transpile --join feature-name.js -o ../static/js  -cw ./js/ModuleNameHere.coffee ./js/OtherModuleName.coffee
```
