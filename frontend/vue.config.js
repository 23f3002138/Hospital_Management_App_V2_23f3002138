const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  
  
  devServer: {
    port: 8080,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
        logLevel: 'debug',
        headers: {
          'Connection': 'keep-alive'
        },
        onProxyReq: (proxyReq, req, res) => {
          
          if (req.headers.authorization) {
            proxyReq.setHeader('Authorization', req.headers.authorization)
          }
        }
      }
    },
    hot: true,
    open: true
  },
  
  
  publicPath: process.env.NODE_ENV === 'production' ? '/hospital-management/' : '/',
  
  
  configureWebpack: {
    resolve: {
      alias: {
        '@': require('path').resolve(__dirname, 'src')
      }
    }
  },
  
  
  css: {
    sourceMap: process.env.NODE_ENV !== 'production'
  },
  
  
  chainWebpack: config => {
    
    config.module
      .rule('svg')
      .exclude.add(require('path').resolve(__dirname, 'src/assets/icons'))
      .end()
    
    config.module
      .rule('icons')
      .test(/\.svg$/)
      .include.add(require('path').resolve(__dirname, 'src/assets/icons'))
      .end()
      .use('svg-sprite-loader')
      .loader('svg-sprite-loader')
      .options({
        symbolId: 'icon-[name]'
      })
      .end()
    
    
    config.performance
      .maxEntrypointSize(512000)
      .maxAssetSize(512000)
  },
  
  
  pwa: {
    name: 'Hospital Management System',
    themeColor: '#007bff',
    msTileColor: '#000000',
    appleMobileWebAppCapable: 'yes',
    appleMobileWebAppStatusBarStyle: 'black',
    
    
    workboxPluginMode: 'InjectManifest',
    workboxOptions: {
      
      swSrc: 'src/sw.js',
      
    }
  },
  
  
  productionSourceMap: false,
  
  
  parallel: require('os').cpus().length > 1
})