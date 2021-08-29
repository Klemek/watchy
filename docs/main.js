/* exported app, utils */

images = ['piece0_0', 'piece0_1',
  'piece1_0', 'piece1_1',
  'piece2_0', 'piece2_1', 'piece2_2', 'piece2_3',
  'piece3_0', 'piece3_1', 'piece3_2', 'piece3_3',
  'piece4_0', 'piece4_1',
  'piece5_0',
  'piece6_0', 'piece6_1', 'piece6_2', 'piece6_3'];

let app = {
  el: '#app',
  data: {
    title: 'Watchy tools',
    tetris_input: '',
    tetris_path: 'img/piece0_0.png'
  },
  methods: {
    compute_tetris: function() {
      const self = this;
      const date = new Date(self.tetris_input);
      const v = Math.floor(self.random_cpp(date) * images.length);
      self.tetris_path = `img/${images[v]}.png`;
    },
    random_cpp: function (date) {
      let seed = date.getFullYear() - 1970;
      seed = seed * 12 + (date.getMonth() + 1);
      seed = seed * 31 + date.getDate();
    
      let v = Math.pow(seed, 6/7);
      v *= (Math.sin(v) + 1);
    
      return v - Math.floor(v);
    },
  },
  watch: {
    tetris_input: 'compute_tetris',
  },
  'mounted': function () {
    const self = this;
    console.log('app mounted');
    setTimeout(() => {
      self.$el.setAttribute('style', '');
    });
    self.tetris_input = (new Date()).toISOString().substr(0, 10);
  }
};

window.onload = () => {
  app = new Vue(app);
};
