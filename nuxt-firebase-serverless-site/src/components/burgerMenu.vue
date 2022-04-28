<template>
    <div>
        <div ref="sideNav" class="bm-menu">
            <nav class="bm-item-list">
                <slot></slot>
            </nav>
            <span @click="closeMenu" :class="{ hidden: !crossIcon }" class="bm-cross-button cross-style">
                <span
                    v-for="(x, index) in 2"
                    :key="x"
                    :style="{
                        position: 'absolute',
                        width: '3px',
                        height: '14px',
                        transform: index === 1 ? 'rotate(45deg)' : 'rotate(-45deg)',
                    }"
                    class="bm-cross"
                >
                </span>
            </span>
        </div>

        <div ref="bmBurgerButton" @click="openMenu" :class="{ hidden: !burgerIcon }" class="bm-burger-button">
            <span
                :style="{ top: 20 * (index * 2) + '%' }"
                v-for="(x, index) in 3"
                :key="index"
                class="bm-burger-bars line-style"
            ></span>
        </div>
    </div>
</template>

<script>
export default {
    name: 'Menubar',
    props: {
        isOpen: {
            type: Boolean,
            required: false,
        },
        right: {
            type: Boolean,
            required: false,
        },
        width: {
            type: [String],
            required: false,
            default: '300',
        },
        disableEsc: {
            type: Boolean,
            required: false,
        },
        noOverlay: {
            type: Boolean,
            required: false,
        },
        onStateChange: {
            type: Function,
            required: false,
            default() {
                return 'banane';
            },
        },
        burgerIcon: {
            type: Boolean,
            required: false,
            default: true,
        },
        crossIcon: {
            type: Boolean,
            required: false,
            default: true,
        },
        disableOutsideClick: {
            type: Boolean,
            required: false,
            default: false,
        },
    },
    data() {
        return {
            isSideBarOpen: false,
        };
    },
    watch: {
        isOpen: {
            deep: true,
            immediate: true,
            handler(newValue, oldValue) {
                this.$nextTick(() => {
                    if (!oldValue && newValue) {
                        this.openMenu();
                    }
                    if (oldValue && !newValue) {
                        this.closeMenu();
                    }
                });
            },
        },
        right: {
            deep: true,
            immediate: true,
            handler(oldValue, newValue) {
                if (oldValue) {
                    this.$nextTick(() => {
                        this.$refs.bmBurgerButton.style.left = 'auto';
                        this.$refs.bmBurgerButton.style.right = '36px';
                        this.$refs.sideNav.style.left = 'auto';
                        this.$refs.sideNav.style.right = '0px';
                        document.querySelector('.bm-burger-button').style.left = 'auto';
                        document.querySelector('.bm-burger-button').style.right = '36px';
                        document.querySelector('.bm-menu').style.left = 'auto';
                        document.querySelector('.bm-menu').style.right = '0px';
                        document.querySelector('.cross-style').style.right = '250px';
                    });
                }
                if (newValue) {
                    if (this.$refs.bmBurgerButton.hasAttribute('style')) {
                        this.$refs.bmBurgerButton.removeAttribute('style');
                        this.$refs.sideNav.style.right = 'auto';
                        document.querySelector('.bm-burger-button').removeAttribute('style');
                        document.getElementById('sideNav').style.right = 'auto';
                        document.querySelector('.cross-style').style.right = '0px';
                    }
                }
            },
        },
    },

    mounted() {
        if (!this.disableEsc) {
            document.addEventListener('keyup', this.closeMenuOnEsc);
        }
    },
    created() {
        /* document.addEventListener('click', this.documentClick); */
    },
    destroyed() {
        document.removeEventListener('keyup', this.closeMenuOnEsc);
        document.removeEventListener('click', this.documentClick);
    },

    methods: {
        openMenu() {
            this.$emit('openMenu');
            this.isSideBarOpen = true;

            if (!this.noOverlay) {
                document.body.classList.add('bm-overlay');
            }
            if (this.right) {
                this.$refs.sideNav.style.left = 'auto';
                this.$refs.sideNav.style.right = '0px';
            }
            this.$nextTick(function() {
                this.$refs.sideNav.style.width = this.width ? this.width + 'px' : '300px';
            });
        },

        closeMenu() {
            this.$emit('closeMenu');
            this.isSideBarOpen = false;
            document.body.classList.remove('bm-overlay');
            this.$refs.sideNav.style.width = '0px';
        },

        closeMenuOnEsc(e) {
            e = e || window.event;
            if (e.key === 'Escape' || e.keyCode === 27) {
                this.closeMenu();
            }
        },
        documentClick(e) {
            const element = this.$refs.bmBurgerButton;
            let target = null;
            if (e && e.target) {
                target = e.target;
            }

            if (
                element &&
                element !== target &&
                !element.contains(target) &&
                e.target.className !== 'bm-menu' &&
                this.isSideBarOpen &&
                !this.disableOutsideClick
            ) {
                this.closeMenu();
            }
        },
    },
};
</script>

<style>
@media screen and (max-width: 767px) {
    html {
        height: 100%;
    }
    .bm-burger-button {
        position: absolute;
        top: 36px;
        left: 36px;
        width: 36px;
        height: 30px;
        cursor: pointer;
    }
    .bm-burger-button.hidden {
        display: none;
    }
    .bm-burger-bars {
        background-color: #373a47;
    }
    .line-style {
        position: absolute;
        right: 0;
        left: 0;
        height: 20%;
    }
    .cross-style {
        position: absolute;
        top: 12px;
        right: 2px;
        cursor: pointer;
    }
    .bm-cross {
        background: #bdc3c7;
    }
    .bm-cross-button {
        width: 24px;
        height: 24px;
    }
    .bm-cross-button.hidden {
        display: none;
    }
    .bm-menu {
        z-index: 1000; /* Stay on top */
        position: fixed; /* Stay in place */
        top: 0;
        left: 0;
        overflow-x: hidden; /* Disable horizontal scroll */
        width: 0; /* 0 width - change this with JavaScript */
        height: 100%; /* 100% Full-height */
        padding-top: 60px; /* Place content 60px from the top */
        background-color: rgb(63, 63, 65); /* Black*/
        transition: 0.5s; /*0.5 second transition effect to slide in the sidenav*/
    }
    .bm-overlay {
        background: rgba(0, 0, 0, 0.3);
    }
    .bm-item-list {
        margin-left: 10%;
        font-size: 20px;
        color: #b8b7ad;
    }
    .bm-item-list > * {
        display: flex;
        padding: 0.7em;
        text-decoration: none;
    }
    .bm-item-list > * > span {
        margin-left: 10px;
        font-weight: 700;
        color: white;
    }
}
</style>
