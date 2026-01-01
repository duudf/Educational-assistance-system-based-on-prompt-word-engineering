<template>
  <assignment-detail :is-edit="false" />
</template>
<script>
import AssignmentDetail from './components/AssignmentDetail'
export default {
  name: 'CreateAssignment',
  components: { AssignmentDetail }
}
</script>
