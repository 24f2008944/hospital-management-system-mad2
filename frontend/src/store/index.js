import { createStore } from 'vuex'
import auth from './modules/auth'
import hospital from './modules/hospital'

export default createStore({
  modules: {
    auth,
    hospital
  }
})
