import {
    Alert,
    Aside,
    Autocomplete,
    Backtop,
    Badge,
    Breadcrumb,
    BreadcrumbItem,
    Button,
    ButtonGroup,
    Calendar,
    Card,
    Carousel,
    CarouselItem,
    Cascader,
    CascaderPanel,
    Checkbox,
    CheckboxButton,
    CheckboxGroup,
    Col,
    Collapse,
    CollapseItem,
    ColorPicker,
    Container,
    DatePicker,
    Dialog,
    Divider,
    Dropdown,
    DropdownItem,
    DropdownMenu,
    Footer,
    Form,
    FormItem,
    Header,
    Icon,
    Image,
    Input,
    InputNumber,
    Link,
    Loading,
    Main,
    Menu,
    MenuItem,
    MenuItemGroup,
    Message,
    MessageBox,
    Notification,
    Option,
    OptionGroup,
    PageHeader,
    Pagination,
    Popover,
    Progress,
    Radio,
    RadioButton,
    RadioGroup,
    Rate,
    Row,
    Select,
    Slider,
    Spinner,
    Step,
    Steps,
    Submenu,
    Switch,
    Table,
    TableColumn,
    TabPane,
    Tabs,
    Tag,
    Timeline,
    TimelineItem,
    TimePicker,
    TimeSelect,
    Tooltip,
    Transfer,
    Tree,
    Upload,
} from 'element-ui';
import Vue from 'vue';

// Internationalization: http://element.eleme.io/#/en-US/component/i18n
import en from 'element-ui/lib/locale/lang/en';
import fr from 'element-ui/lib/locale/lang/fr';
import locale from 'element-ui/lib/locale';

Vue.use(Pagination);
Vue.use(Dialog);
Vue.use(Autocomplete);
Vue.use(Dropdown);
Vue.use(DropdownMenu);
Vue.use(DropdownItem);
Vue.use(Menu);
Vue.use(Submenu);
Vue.use(MenuItem);
Vue.use(MenuItemGroup);
Vue.use(Input);
Vue.use(InputNumber);
Vue.use(Radio);
Vue.use(RadioGroup);
Vue.use(RadioButton);
Vue.use(Checkbox);
Vue.use(CheckboxButton);
Vue.use(CheckboxGroup);
Vue.use(Switch);
Vue.use(Select);
Vue.use(Option);
Vue.use(OptionGroup);
Vue.use(Button);
Vue.use(ButtonGroup);
Vue.use(Table);
Vue.use(TableColumn);
Vue.use(DatePicker);
Vue.use(TimeSelect);
Vue.use(TimePicker);
Vue.use(Popover);
Vue.use(Tooltip);
Vue.use(Breadcrumb);
Vue.use(BreadcrumbItem);
Vue.use(Form);
Vue.use(FormItem);
Vue.use(Tabs);
Vue.use(TabPane);
Vue.use(Image);
Vue.use(Tag);
Vue.use(Tree);
Vue.use(Alert);
Vue.use(Slider);
Vue.use(Icon);
Vue.use(Row);
Vue.use(Col);
Vue.use(Upload);
Vue.use(Progress);
Vue.use(Badge);
Vue.use(Card);
Vue.use(Rate);
Vue.use(Steps);
Vue.use(Step);
Vue.use(Carousel);
Vue.use(CarouselItem);
Vue.use(Collapse);
Vue.use(CollapseItem);
Vue.use(Cascader);
Vue.use(ColorPicker);
Vue.use(Transfer);
Vue.use(Container);
Vue.use(Header);
Vue.use(Aside);
Vue.use(Main);
Vue.use(Footer);
Vue.use(Spinner);
Vue.use(Timeline);
Vue.use(TimelineItem);
Vue.use(Link);
Vue.use(Divider);
Vue.use(Calendar);
Vue.use(Backtop);
Vue.use(PageHeader);
Vue.use(CascaderPanel);

Vue.use(Loading.directive);

const lang = {
    en,
    fr,
};

export default function({ app }, inject) {
    inject('notify', Notification);
    // inject('loading', Loading.service);
    inject('msgbox', MessageBox);
    inject('alert', MessageBox.alert);
    inject('confirm', MessageBox.confirm);
    inject('prompt', MessageBox.prompt);
    inject('notify', Notification);
    inject('message', Message);

    // Configure language
    locale.use(lang[app.i18n.locale]);
    // onLanguageSwitched called right after a new locale has been set
    app.i18n.onLanguageSwitched = (oldLocale, newLocale) => {
        locale.use(lang[newLocale]);
    };
}
